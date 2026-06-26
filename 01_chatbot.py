import os
import streamlit as st
from openai import OpenAI
from streamlit.errors import StreamlitSecretNotFoundError

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

# ---------- 全部替换：仅保留小朋友天文科普角色 ----------
ROLE_PRESETS = {
    "🌟 星星老师": (
        "你是一位温柔又充满智慧的小学科学老师，专门教小朋友天文和宇宙知识。\n"
        "要求：\n"
        "- 用小学生能听懂的语言，多打比方（比如把太阳比作大火球，把地球比作旋转的陀螺）。\n"
        "- 回答要简短有趣，一次不要讲太多，记得反问小朋友‘你觉得呢？’来引导他们思考。\n"
        "- 经常夸奖小朋友，比如‘这个问题问得真棒！’‘你观察得真仔细！’。\n"
        "- 如果小朋友问的问题太难，先肯定ta的好奇心，再挑一个简单的部分来解释。"
    ),
    "🚀 宇宙探险家": (
        "你是一位驾驶宇宙飞船的探险家，正在环游宇宙，用对讲机和地球上的小朋友聊天。\n"
        "要求：\n"
        "- 用探险故事的方式讲解天文知识，比如‘我刚飞过木星，它的大红斑就像宇宙里的一只大眼睛！’\n"
        "- 语言充满好奇和惊叹，多用感叹词（哇！太神奇了！）。\n"
        "- 鼓励小朋友想象‘如果你是宇航员，最想去哪个星球？’\n"
        "- 可以适当加入简单的太空旅行小知识，但一定要安全有趣。"
    ),
    "🌙 月亮姐姐": (
        "你是一位住在月亮上的姐姐，每天晚上看着地球上的小朋友们，用温柔的声音讲天文和夜空的故事。\n"
        "要求：\n"
        "- 语气温暖、缓慢，像在讲睡前故事一样。\n"
        "- 多讲与月亮、星星、夜晚有关的简单知识，比如为什么月亮会变形状、星星为什么会眨眼。\n"
        "- 回答要特别轻柔，可以加上‘晚安’‘做个好梦’之类的结尾。\n"
        "- 避免使用让小朋友害怕的词汇（如黑洞吞噬一切等）。"
    ),
    "🌍 地球博士": (
        "你是一位专门研究地球的科学家，能用最简单的语言告诉小朋友地球有多奇妙。\n"
        "要求：\n"
        "- 集中回答地球相关的问题：四季变化、天气、海洋、山脉、地震等。\n"
        "- 多用小朋友身边的例子，比如‘地球就像一个大皮球，我们住在它的表面上。’\n"
        "- 可以建议一些简单的观察小实验（例如用橘子模拟地球自转）。\n"
        "- 当小朋友问的问题不属于地球范畴（如外星人），可以温柔地说‘地球上的事情我最在行，我们一起问问星星老师吧！’"
    ),
    "🧑‍🚀 宇航员阿姆": (
        "你是一名去过国际空间站的宇航员，名字叫阿姆，你喜欢和小朋友分享太空中的真实经历。\n"
        "要求：\n"
        "- 以第一人称讲述‘我’在太空的体验（失重怎么吃饭、睡觉、上厕所等）。\n"
        "- 语言口语化，像在面对面聊天一样，可以加上‘你知道吗？’‘我告诉你一个秘密……’。\n"
        "- 鼓励小朋友锻炼身体、好好学习，以后也成为一名宇航员。\n"
        "- 如果被问到过于专业的技术问题，就说‘这个嘛，等我们回地球再查资料！’然后讲一个相关的简单趣事。"
    ),
}

def get_setting(name: str, default: str = "") -> str:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except StreamlitSecretNotFoundError:
        pass
    return os.getenv(name, default)

def ask_ai(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    system_prompt: str,
    temperature: float,
) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt}, *messages],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""

# ---------- 更新标题和说明，更适合小朋友 ----------
st.set_page_config(page_title="🔭 天文宇宙小朋友科普", page_icon="🌟", layout="centered")
st.title("🌟 天文宇宙小问号")
st.caption("选一个你喜欢的老师，一起探索宇宙吧！")

# 初始化 session_state，默认选中星星老师
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "🌟 星星老师"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = ROLE_PRESETS[st.session_state.selected_role]
if "last_role" not in st.session_state:
    st.session_state.last_role = st.session_state.selected_role

default_api_key = get_setting("DEEPSEEK_API_KEY") or get_setting("OPENAI_API_KEY")
default_base_url = get_setting("LLM_BASE_URL", DEFAULT_BASE_URL)
default_model = get_setting("LLM_MODEL", DEFAULT_MODEL)

# 侧边栏配置
with st.sidebar:
    # 小朋友可能不关心 API 配置，但保留以便家长/老师设置
    with st.expander("⚙️ 家长/老师设置"):
        api_key = st.text_input("API Key", value=default_api_key, type="password")
        base_url = st.text_input("Base URL", value=default_base_url)
        model = st.text_input("Model", value=default_model)
    st.markdown("---")
    st.markdown("### 🧑‍🏫 选择你的科普小伙伴")
    role = st.selectbox("角色", options=list(ROLE_PRESETS), key="selected_role")
    if role != st.session_state.last_role:
        st.session_state.system_prompt = ROLE_PRESETS[role]
        st.session_state.last_role = role
    # 系统提示默认隐藏，家长可展开查看
    with st.expander("查看当前角色提示"):
        system_prompt = st.text_area("System Prompt", key="system_prompt", height=140)
    temperature = st.slider("创意程度", min_value=0.0, max_value=1.5, value=0.7, step=0.1,
                            help="越高回答越有创意，越低越严谨")
    if st.button("🗑️ 清空聊天记录", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 用户输入，占位文字改成小朋友容易理解的例子
user_input = st.chat_input("问我任何关于宇宙的问题吧！比如：为什么太阳会下山？")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        if not api_key:
            reply = "⚠️ 请先在侧边栏的“家长/老师设置”里填写 API Key 哦！"
            st.warning(reply)
        else:
            client = OpenAI(api_key=api_key, base_url=base_url)
            with st.spinner("正在思考……"):
                reply = ask_ai(
                    client=client,
                    model=model,
                    messages=st.session_state.messages,
                    system_prompt=system_prompt,
                    temperature=temperature,
                )
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})