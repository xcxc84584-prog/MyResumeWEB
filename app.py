import json, os, uuid
from datetime import date
from pathlib import Path
import streamlit as st
from sqlalchemy import case
from sqlalchemy.exc import IntegrityError
from backend.database import Base, engine, SessionLocal
from backend.security import hash_password, verify_password
from backend.models.user import User
from backend.models.profile import Profile
from backend.models.skill import Skill
from backend.models.certificate import Certificate
from backend.models.document import Document
from backend.models.reviewer_account import ReviewerAccount
from backend.models.resume_submission import ResumeSubmission

ROOT=Path(__file__).resolve().parent
UPLOAD_DOC=ROOT/'storage'/'uploads'/'documents'
UPLOAD_AVATAR=ROOT/'storage'/'uploads'/'avatars'
UPLOAD_DOC.mkdir(parents=True,exist_ok=True); UPLOAD_AVATAR.mkdir(parents=True,exist_ok=True)
Base.metadata.create_all(bind=engine)
st.set_page_config(page_title='ResumeSystem',page_icon='📄',layout='wide')
STATUS_TEXT={'unread':'未讀','backup':'備選','accepted':'正取','rejected':'落選'}
DURATION={'less_than_30_days':'少於 30 天','one_month':'1 個月','three_months':'3 個月','six_months':'6 個月','over_one_year':'超過 1 年'}
LEVEL={'beginner':'初階','intermediate':'中階','advanced':'進階'}
EDU={'high_school':'高中','vocational_school':'高職','associate':'專科','bachelor':'學士','master':'碩士','doctorate':'博士','other':'其他'}

def db(): return SessionLocal()
def rerun(): st.rerun()
def login_state(kind,id): st.session_state.auth_kind=kind; st.session_state.auth_id=id
def logout():
    for k in ['auth_kind','auth_id']: st.session_state.pop(k,None)
    rerun()
def current_user(s):
    if st.session_state.get('auth_kind')!='user': return None
    return s.query(User).filter(User.id==st.session_state.get('auth_id')).first()
def current_reviewer(s):
    if st.session_state.get('auth_kind')!='reviewer': return None
    return s.query(ReviewerAccount).filter(ReviewerAccount.id==st.session_state.get('auth_id')).first()
def age(b):
    if not b:return None
    t=date.today(); return t.year-b.year-((t.month,t.day)<(b.month,b.day))
def save_upload(up,folder):
    ext=Path(up.name).suffix.lower(); name=f'{uuid.uuid4().hex}{ext}'; p=folder/name
    p.write_bytes(up.getvalue()); return name,str(p),len(up.getvalue())
def file_bytes(path):
    p=Path(path)
    if not p.is_absolute(): p=ROOT/p
    return p.read_bytes() if p.exists() else None
def build_resume(u,s):
    p=s.query(Profile).filter(Profile.user_id==u.id).first()
    skills=s.query(Skill).filter(Skill.user_id==u.id).order_by(Skill.id).all()
    certs=s.query(Certificate).filter(Certificate.user_id==u.id).order_by(Certificate.id).all()
    return {'username':u.username,'profile':({'full_name':p.full_name,'gender':p.gender,'birth_date':str(p.birth_date) if p.birth_date else None,'age':age(p.birth_date),'phone':p.phone,'education_level':p.education_level,'avatar_path':p.avatar_path} if p else None),'skills':[{'id':x.id,'skill_name':x.skill_name,'learning_duration':x.learning_duration,'proficiency_level':x.proficiency_level,'documents':[{'id':d.id,'original_filename':d.original_filename,'file_path':d.file_path,'content_type':d.content_type,'file_size':d.file_size} for d in x.documents]} for x in skills],'certificates':[{'id':x.id,'certificate_name':x.certificate_name,'issuer':x.issuer,'issue_date':str(x.issue_date) if x.issue_date else None,'expiration_date':str(x.expiration_date) if x.expiration_date else None,'certificate_number':x.certificate_number,'documents':[{'id':d.id,'original_filename':d.original_filename,'file_path':d.file_path,'content_type':d.content_type,'file_size':d.file_size} for d in x.documents]} for x in certs]}
def render_resume(data, allow_files=True):
    p=data.get('profile')
    c1,c2=st.columns([1,4])
    with c1:
        if p and p.get('avatar_path'):
            b=file_bytes(p['avatar_path'])
            if b: st.image(b,width=150)
    with c2:
        st.title((p or {}).get('full_name') or data.get('username','履歷'))
        st.caption(f"帳號：{data.get('username','')}" )
        if p:
            st.write(f"年齡：{p.get('age') or '—'}　｜　電話：{p.get('phone') or '—'}　｜　學歷：{EDU.get(p.get('education_level'),p.get('education_level') or '—')}")
    st.subheader('技能')
    if not data.get('skills'): st.info('尚未新增技能')
    for x in data.get('skills',[]):
        with st.expander(x['skill_name'],expanded=True):
            st.write(f"學習時間：{DURATION.get(x.get('learning_duration'),x.get('learning_duration'))}　｜　熟練度：{LEVEL.get(x.get('proficiency_level'),x.get('proficiency_level'))}")
            if allow_files:
                for d in x.get('documents',[]):
                    b=file_bytes(d.get('file_path',''))
                    if b: st.download_button(f"附件：{d['original_filename']}",b,d['original_filename'],key=f"rd-s-{x['id']}-{d['id']}")
    st.subheader('證照')
    if not data.get('certificates'): st.info('尚未新增證照')
    for x in data.get('certificates',[]):
        with st.expander(x['certificate_name'],expanded=True):
            st.write(f"發證單位：{x.get('issuer') or '—'}　｜　證號：{x.get('certificate_number') or '—'}")
            st.write(f"取得日期：{x.get('issue_date') or '—'}　｜　到期日期：{x.get('expiration_date') or '—'}")
            if allow_files:
                for d in x.get('documents',[]):
                    b=file_bytes(d.get('file_path',''))
                    if b: st.download_button(f"附件：{d['original_filename']}",b,d['original_filename'],key=f"rd-c-{x['id']}-{d['id']}")
def public_page(s):
    st.title('ResumeSystem')
    st.write('建立、管理與投遞履歷；企業批閱帳號可接收履歷並更新審核狀態。')
    a,b=st.tabs(['一般使用者','批閱帳號'])
    with a:
        l,r=st.columns(2)
        with l:
            st.subheader('登入')
            with st.form('ulogin'):
                un=st.text_input('使用者名稱'); pw=st.text_input('密碼',type='password')
                if st.form_submit_button('登入',use_container_width=True):
                    u=s.query(User).filter(User.username==un.strip()).first()
                    if u and verify_password(pw,u.password_hash): login_state('user',u.id); rerun()
                    else: st.error('帳號或密碼錯誤')
        with r:
            st.subheader('註冊')
            with st.form('ureg'):
                un=st.text_input('使用者名稱',key='ru'); em=st.text_input('Email'); p1=st.text_input('密碼',type='password',key='rp1'); p2=st.text_input('確認密碼',type='password')
                if st.form_submit_button('建立帳號',use_container_width=True):
                    if not un.strip() or not em.strip() or len(p1)<8 or p1!=p2: st.error('請完整填寫；密碼至少 8 碼且兩次需一致')
                    elif s.query(User).filter((User.username==un.strip())|(User.email==em.strip())).first(): st.error('使用者名稱或 Email 已存在')
                    else:
                        u=User(username=un.strip(),email=em.strip(),password_hash=hash_password(p1)); s.add(u); s.commit(); st.success('註冊成功，請登入')
    with b:
        l,r=st.columns(2)
        with l:
            st.subheader('批閱帳號登入')
            with st.form('rlogin'):
                co=st.text_input('公司名稱'); de=st.text_input('帳號描述'); pw=st.text_input('密碼',type='password',key='rlp')
                if st.form_submit_button('登入',use_container_width=True):
                    x=s.query(ReviewerAccount).filter(ReviewerAccount.company_name==co.strip(),ReviewerAccount.description==de.strip()).first()
                    if x and verify_password(pw,x.password_hash): login_state('reviewer',x.id); rerun()
                    else: st.error('批閱帳號資料錯誤')
        with r:
            st.subheader('建立批閱帳號')
            with st.form('rreg'):
                co=st.text_input('公司名稱',key='rco'); de=st.text_input('帳號描述',key='rde'); pw=st.text_input('密碼（至少 8 碼）',type='password',key='rrp')
                if st.form_submit_button('建立',use_container_width=True):
                    if not co.strip() or not de.strip() or len(pw)<8: st.error('資料不完整')
                    elif s.query(ReviewerAccount).filter(ReviewerAccount.company_name==co.strip(),ReviewerAccount.description==de.strip()).first(): st.error('此公司名稱＋描述已存在')
                    else:
                        x=ReviewerAccount(company_name=co.strip(),description=de.strip(),password_hash=hash_password(pw)); s.add(x); s.commit(); st.success('建立成功')
def user_page(s,u):
    st.sidebar.title('ResumeSystem'); st.sidebar.write(f'👤 {u.username}')
    page=st.sidebar.radio('功能',['總覽','個人資料','技能','證照','文件','履歷預覽','投遞履歷','帳號'])
    st.sidebar.button('登出',on_click=logout,use_container_width=True)
    if page=='總覽':
        st.title('使用者總覽'); st.metric('技能',s.query(Skill).filter(Skill.user_id==u.id).count()); st.metric('證照',s.query(Certificate).filter(Certificate.user_id==u.id).count()); st.metric('文件',s.query(Document).filter(Document.user_id==u.id).count())
    elif page=='個人資料':
        st.title('個人資料'); p=s.query(Profile).filter(Profile.user_id==u.id).first()
        if p and p.avatar_path:
            b=file_bytes(p.avatar_path)
            if b: st.image(b,width=140)
        avatar=st.file_uploader('大頭貼',type=['jpg','jpeg','png','webp'])
        with st.form('profile'):
            full=st.text_input('姓名',value=p.full_name if p else '')
            gender=st.selectbox('性別',['','male','female','other','prefer_not_to_say'],index=(['','male','female','other','prefer_not_to_say'].index(p.gender) if p and p.gender in ['male','female','other','prefer_not_to_say'] else 0))
            phone=st.text_input('電話',value=p.phone or '' if p else '')
            edu_opts=['','high_school','vocational_school','associate','bachelor','master','doctorate','other']; edu=st.selectbox('學歷',edu_opts,index=(edu_opts.index(p.education_level) if p and p.education_level in edu_opts else 0),format_func=lambda x:EDU.get(x,'—'))
            birth=st.date_input('生日',value=p.birth_date if p and p.birth_date else date(2000,1,1),min_value=date(1900,1,1),max_value=date.today())
            if st.form_submit_button('儲存'):
                if not full.strip(): st.error('姓名不可空白')
                else:
                    if not p: p=Profile(user_id=u.id,full_name=full.strip()); s.add(p)
                    p.full_name=full.strip(); p.gender=gender or None; p.phone=phone.strip() or None; p.education_level=edu or None; p.birth_date=birth
                    if avatar:
                        name,path,_=save_upload(avatar,UPLOAD_AVATAR); p.avatar_path=path
                    s.commit(); st.success('已儲存'); rerun()
    elif page=='技能':
        st.title('技能')
        with st.form('addskill'):
            n=st.text_input('技能名稱'); d=st.selectbox('學習時間',list(DURATION),format_func=lambda x:DURATION[x]); lv=st.selectbox('熟練度',list(LEVEL),format_func=lambda x:LEVEL[x])
            if st.form_submit_button('新增技能') and n.strip(): s.add(Skill(user_id=u.id,skill_name=n.strip(),learning_duration=d,proficiency_level=lv)); s.commit(); rerun()
        for x in s.query(Skill).filter(Skill.user_id==u.id).order_by(Skill.id).all():
            c1,c2=st.columns([5,1]); c1.write(f"**{x.skill_name}** — {DURATION.get(x.learning_duration)} / {LEVEL.get(x.proficiency_level)}")
            if c2.button('刪除',key=f'ds{x.id}'): s.delete(x); s.commit(); rerun()
    elif page=='證照':
        st.title('證照')
        with st.form('addcert'):
            n=st.text_input('證照名稱'); issuer=st.text_input('發證單位'); num=st.text_input('證照號碼'); hasdate=st.checkbox('填寫取得日期'); issued=st.date_input('取得日期')
            if st.form_submit_button('新增證照') and n.strip(): s.add(Certificate(user_id=u.id,certificate_name=n.strip(),issuer=issuer.strip() or None,certificate_number=num.strip() or None,issue_date=issued if hasdate else None)); s.commit(); rerun()
        for x in s.query(Certificate).filter(Certificate.user_id==u.id).order_by(Certificate.id).all():
            c1,c2=st.columns([5,1]); c1.write(f"**{x.certificate_name}** — {x.issuer or '—'}")
            if c2.button('刪除',key=f'dc{x.id}'): s.delete(x); s.commit(); rerun()
    elif page=='文件':
        st.title('文件管理'); up=st.file_uploader('上傳 PDF / 圖片 / ZIP',type=['pdf','jpg','jpeg','png','webp','zip'])
        if up and st.button('上傳文件'):
            name,path,size=save_upload(up,UPLOAD_DOC); s.add(Document(user_id=u.id,original_filename=up.name,stored_filename=name,file_path=path,content_type=up.type or 'application/octet-stream',file_size=size)); s.commit(); rerun()
        docs=s.query(Document).filter(Document.user_id==u.id).order_by(Document.id).all(); skills=s.query(Skill).filter(Skill.user_id==u.id).all(); certs=s.query(Certificate).filter(Certificate.user_id==u.id).all()
        for d in docs:
            with st.expander(d.original_filename):
                b=file_bytes(d.file_path)
                if b: st.download_button('下載',b,d.original_filename,key=f'dl{d.id}')
                sk=st.multiselect('連結到技能',skills,default=d.skills,format_func=lambda x:x.skill_name,key=f'sk{d.id}'); ce=st.multiselect('連結到證照',certs,default=d.certificates,format_func=lambda x:x.certificate_name,key=f'ce{d.id}')
                if st.button('儲存連結',key=f'link{d.id}'): d.skills=sk; d.certificates=ce; s.commit(); st.success('已更新')
                if st.button('刪除文件',key=f'dd{d.id}'):
                    p=Path(d.file_path); s.delete(d); s.commit();
                    if p.exists(): p.unlink()
                    rerun()
    elif page=='履歷預覽': st.title('履歷預覽'); render_resume(build_resume(u,s))
    elif page=='投遞履歷':
        st.title('投遞履歷'); q=st.text_input('搜尋公司名稱或描述')
        query=s.query(ReviewerAccount)
        if q.strip(): query=query.filter((ReviewerAccount.company_name.ilike(f'%{q.strip()}%'))|(ReviewerAccount.description.ilike(f'%{q.strip()}%')))
        for r in query.order_by(ReviewerAccount.company_name).limit(20).all():
            existing=s.query(ResumeSubmission).filter(ResumeSubmission.applicant_user_id==u.id,ResumeSubmission.reviewer_account_id==r.id).first()
            c1,c2=st.columns([5,1]); c1.write(f"**{r.company_name}** — {r.description}")
            if existing: c2.write(STATUS_TEXT.get(existing.status,existing.status))
            elif c2.button('投遞',key=f'sub{r.id}'):
                snap=json.dumps(build_resume(u,s),ensure_ascii=False,default=str); s.add(ResumeSubmission(applicant_user_id=u.id,reviewer_account_id=r.id,status='unread',resume_snapshot=snap)); s.commit(); rerun()
        st.subheader('我的投遞')
        for x in s.query(ResumeSubmission).filter(ResumeSubmission.applicant_user_id==u.id).order_by(ResumeSubmission.submitted_at.desc()).all():
            c1,c2=st.columns([5,1]); c1.write(f"{x.reviewer_account.company_name} — **{STATUS_TEXT.get(x.status,x.status)}** — {x.submitted_at:%Y-%m-%d %H:%M}")
            if c2.button('撤回',key=f'wd{x.id}'): s.delete(x); s.commit(); rerun()
    else:
        st.title('帳號'); st.write(u.email); st.warning('註銷帳號會永久刪除帳號與相關資料。')
        pw=st.text_input('輸入密碼確認',type='password')
        if st.button('註銷一般帳號'):
            if verify_password(pw,u.password_hash): s.delete(u); s.commit(); logout()
            else: st.error('密碼錯誤')
def reviewer_page(s,r):
    st.sidebar.title(r.company_name); st.sidebar.caption(r.description); page=st.sidebar.radio('功能',['收到的履歷','帳號']); st.sidebar.button('登出',on_click=logout,use_container_width=True)
    if page=='收到的履歷':
        st.title('履歷批閱')
        order=case((ResumeSubmission.status=='unread',1),(ResumeSubmission.status=='backup',2),(ResumeSubmission.status=='accepted',3),(ResumeSubmission.status=='rejected',4),else_=5)
        subs=s.query(ResumeSubmission).filter(ResumeSubmission.reviewer_account_id==r.id).order_by(order,ResumeSubmission.submitted_at.desc()).all()
        if not subs: st.info('目前沒有收到履歷')
        labels={x.id:f"#{x.id} {x.applicant.username}｜{STATUS_TEXT.get(x.status,x.status)}｜{x.submitted_at:%Y-%m-%d %H:%M}" for x in subs}
        if subs:
            sid=st.selectbox('選擇履歷',[x.id for x in subs],format_func=lambda x:labels[x]); x=next(z for z in subs if z.id==sid)
            new=st.selectbox('批閱狀態',list(STATUS_TEXT),index=list(STATUS_TEXT).index(x.status),format_func=lambda v:STATUS_TEXT[v])
            if st.button('儲存狀態'):
                x.status=new; s.commit(); st.success('狀態已保存'); rerun()
            st.divider(); render_resume(json.loads(x.resume_snapshot))
    else:
        st.title('批閱帳號'); st.warning('註銷後會刪除所有與此批閱帳號相關的投遞紀錄。'); pw=st.text_input('輸入密碼確認',type='password')
        if st.button('註銷批閱帳號'):
            if verify_password(pw,r.password_hash): s.delete(r); s.commit(); logout()
            else: st.error('密碼錯誤')

def main():
    s=db()
    try:
        kind=st.session_state.get('auth_kind')
        if kind=='user':
            u=current_user(s)
            if u:user_page(s,u)
            else: logout()
        elif kind=='reviewer':
            r=current_reviewer(s)
            if r:reviewer_page(s,r)
            else: logout()
        else: public_page(s)
    finally:s.close()
if __name__=='__main__': main()
