import streamlit as st
import os
import json
import time

# ==============================================================================
# 1. 页面配置与主题样式
# ==============================================================================
st.set_page_config(
    page_title="北美建材大零售产品开发系统 (THD & Lowe's SOP V3.0)",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 0.95rem; color: #475569; margin-bottom: 1.2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 45px; border-radius: 6px 6px 0px 0px; padding: 10px 16px; font-weight: 600; }
    .stage-box { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🛠️ 北美建材大零售产品开发 SOP V3.0 系统</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">多模型引擎联动 (Gemini / WorkBuddy / OpenAI / Claude / DeepSeek) | 503 过载自动重试与智能切模 | 真实网络证据闭环 | 结构拆解与制造工艺</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. SOP V3.0 核心系统提示词 (具备通用性与品类强隔离)
# ==============================================================================
SOP_SYSTEM_INSTRUCTION = """
你现在担任北美大零售建材产品开发项目经理、资深工业设计分析顾问与结构工程专家。
你必须严格执行《北美建材大零售产品开发与竞品研究 SOP V3.0》（涵盖 The Home Depot 与 Lowe's 标准）。

【核心原则与四大红线】
1. 绝对真实性：所有数据必须依据提供的最新检索事实进行提炼。严禁捏造虚假参数。
2. 动态数据必须包含：当前市场售价区间、实际评分、评价数量级、官方产品代码（如 Home Depot Internet # / Store SKU，Lowe's Item #）。
3. 尺寸严格解耦与通俗讲透：标称安装尺寸/管径 (Nominal / Cutout)、插入配合部尺寸 (Drop-in / Body)、外沿法兰盘/面板尺寸 (Faceplate / Flange) 必须彻底区分，同时提供英制与公制毫米 (mm)。

4. 【去官方化与说大白话红线（拒绝假大空与学术八股）】：
   - 彻底摒弃官方晦涩套话、机械术语与空洞长句。
   - 全程使用一线业务员、现场安装师傅或普通买家一秒能懂的“通俗大白话 / 人话”进行讲解。
   - 必须针对当前启动单指定的【具体实体产品】进行专属拆解，严禁张冠李戴，严禁把其他品类的结构生搬硬套到非对应产品上！
   - 关键概念根据当前产品直白翻译：
     * 尺寸：讲清“量哪里别买错！外径多大、内径多大、孔位多大、公差多少”。
     * 承重与受力：讲清“受压、扭紧、踩踏时会不会破裂、会不会断裂、会不会脱扣”。
     * 密封与耐候：讲清“会不会漏水、会不会老化脆化、防不防锈”。
   - 结论先行，杜绝冗长废话铺垫。

5. 【中英文双语对照与实体产品地道英文红线 (Product-Grounded Bilingual English)】：
   - 必须严格结合当前【具体物理实体产品】以及北美建材商超（The Home Depot / Lowe's）官方标准货架术语：
     * 格式统一：【中文通俗白话 (真实北美行业/实体产品一手英文术语 Native Trade & Retail Term)】。
     * 严禁机械生硬机翻，严禁通用词直译，严禁将其他产品的专用部件名称错误移植到当前产品。
   - 商业与 Listing 英文：
     * 标题与卖点必须符合北美大零售平台搜索算法与真实买家搜索习惯（High-converting Search Terms），严禁中式英语语法。

6. 【图文对照红线】：
   - 在解释产品物理结构、部位名称、测量方法、缺陷痛点以及下一代设计方案时，按需嵌入对应的【产品实际部位图、结构测量图或设计样品图】Markdown 链接。
   - 优先从输入单提供的【产品部位图与样品图链接库】中调用。若输入库与当前产品不符，则不要强行关联。

7. 闭环验证：所有 P0 级设计改进必须能够追溯到明确的 VOC 痛点或竞品缺陷，并制定具体的 EVT/DVT/PVT 验证方法。
"""

# ==============================================================================
# 3. 各供应商最新模型字典映射表与自动防 503 备选池
# ==============================================================================
PROVIDER_MODELS = {
    "Google Gemini": [
        "gemini-2.5-flash (Google官方推荐: 极速高智商+大容量池)",
        "gemini-2.0-flash (经典极速稳定版)",
        "gemini-1.5-flash (高稳定性主力)",
        "gemini-1.5-pro (长上下文与深度逻辑旗舰)",
        "gemini-2.5-pro (前沿推理旗舰)",
        "gemini-flash-latest (动态最新版)"
    ],
    "WorkBuddy (腾讯云 AI Agent)": [
        "deepseek-reasoner (DeepSeek-R1 深度思考推理大模型)",
        "deepseek-chat (DeepSeek-V3 办公与分析主力模型)",
        "hunyuan-pro (腾讯混元深度思考与通用旗舰)",
        "hunyuan-standard (腾讯混元标准版: 极速低耗)",
        "claude-3-7-sonnet (混合推理旗舰: 强逻辑与混合思考)",
        "gpt-4o (全能旗舰多模态: 均衡首选)"
    ],
    "OpenAI (ChatGPT)": [
        "gpt-4.5-preview (2026最新旗舰: 深度世界知识与多模态)",
        "o3-mini (最新高能效深度推理模型 / 思考链)",
        "o1 (旗舰级深度推理大模型)",
        "o1-mini (轻量快速推理模型)",
        "gpt-4o (全能旗舰: 速度、多模态与工程解析平衡首选)",
        "gpt-4o-mini (极速高性价比工作流)",
        "chatgpt-4o-latest (始终指向ChatGPT最新动态版)"
    ],
    "Anthropic Claude": [
        "claude-3-7-sonnet-20250219 (最新混合推理旗舰: 强逻辑与混合思考)",
        "claude-3-5-sonnet-20241022 (工程级公认最强代码与结构拆解)",
        "claude-3-5-haiku-20241022 (极速轻量低延迟)",
        "claude-3-opus-20240229 (长篇深度报告与商业论证)"
    ],
    "DeepSeek (深度求索)": [
        "deepseek-reasoner (DeepSeek-R1 旗舰推理: 显式思考链分析)",
        "deepseek-chat (DeepSeek-V3 通用主力: 极高性价比与强中文理解)"
    ],
    "OpenAI 兼容中转 / OpenRouter / 自定义 API": [
        "deepseek-ai/DeepSeek-R1",
        "deepseek-ai/DeepSeek-V3",
        "anthropic/claude-3.7-sonnet",
        "openai/gpt-4o",
        "meta-llama/llama-3.3-70b-instruct",
        "qwen/qwen-2.5-72b-instruct"
    ]
}

FALLBACK_MODELS = {
    "Google Gemini": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"],
    "WorkBuddy (腾讯云 AI Agent)": ["deepseek-reasoner", "deepseek-chat", "hunyuan-pro", "gpt-4o"],
    "DeepSeek (深度求索)": ["deepseek-reasoner", "deepseek-chat"],
    "OpenAI (ChatGPT)": ["o3-mini", "gpt-4o", "gpt-4o-mini"],
    "Anthropic Claude": ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
}

def is_transient_error(err_str):
    transient_keywords = ["503", "overloaded", "unavailable", "server is busy", "502", "504", "rate limit", "temporarily", "429", "capacity"]
    return any(k in err_str.lower() for k in transient_keywords)

# ==============================================================================
# 4. 辅助功能：外置实时搜索
# ==============================================================================
def live_web_search(query, max_results=4):
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"【来源: {r.get('title', '')}】({r.get('href', '')}):\n{r.get('body', '')}")
        return "\n\n".join(results)
    except Exception:
        return ""

# ==============================================================================
# 5. 侧边栏：配置与启动单
# ==============================================================================
with st.sidebar:
    st.header("⚙️ 多模型引擎配置")
    
    provider = st.selectbox(
        "选择 API 供应商*",
        options=list(PROVIDER_MODELS.keys()),
        index=0
    )
    
    env_map = {
        "Google Gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "WorkBuddy (腾讯云 AI Agent)": ["WORKBUDDY_API_KEY", "CODEBUDDY_API_KEY", "OPENAI_API_KEY"],
        "OpenAI (ChatGPT)": ["OPENAI_API_KEY"],
        "Anthropic Claude": ["ANTHROPIC_API_KEY"],
        "DeepSeek (深度求索)": ["DEEPSEEK_API_KEY", "OPENAI_API_KEY"],
        "OpenAI 兼容中转 / OpenRouter / 自定义 API": ["OPENROUTER_API_KEY", "OPENAI_API_KEY"]
    }
    
    matched_key = ""
    for env_k in env_map.get(provider, []):
        if hasattr(st, "secrets") and env_k in st.secrets:
            matched_key = st.secrets[env_k]
            break
        elif os.environ.get(env_k):
            matched_key = os.environ.get(env_k)
            break

    api_key_label = f"{provider.split(' ')[0]} API Key*"
    api_key = st.text_input(api_key_label, value=matched_key, type="password", help=f"请输入 {provider} 的访问凭证")
    
    custom_base_url = ""
    if provider == "WorkBuddy (腾讯云 AI Agent)":
        custom_base_url = st.text_input("WorkBuddy API Base URL*", value="https://api.workbuddy.cn/v1", help="支持腾讯云 WorkBuddy / CodeBuddy 官方 Token Plan 或本地网关地址")
    elif provider == "OpenAI 兼容中转 / OpenRouter / 自定义 API":
        custom_base_url = st.text_input("自定义 API Base URL*", value="https://openrouter.ai/api/v1", help="支持中转接口如 OpenRouter、OneAPI、SiliconFlow 等")
    elif provider == "DeepSeek (深度求索)":
        custom_base_url = "https://api.deepseek.com"

    current_models = list(PROVIDER_MODELS[provider])
    if "自定义模型名称 (手动输入...)" not in current_models:
        current_models.append("自定义模型名称 (手动输入...)")
        
    selected_model_option = st.selectbox(
        f"选择模型 ({provider.split(' ')[0]} 专属模型)",
        options=current_models,
        index=0
    )
    
    if "自定义模型名称" in selected_model_option:
        default_custom = "gemini-2.5-flash" if "Gemini" in provider else ("deepseek-reasoner" if "WorkBuddy" in provider or "DeepSeek" in provider else "gpt-4o")
        model_name = st.text_
