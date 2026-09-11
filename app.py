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
# 2. SOP V3.0 核心系统提示词 (强制真实性与可核验超链接)
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

7. 【真实性证据链与必须提供可核验超链接红线 (Zero-Hallucination & Mandatory Hyperlinks)】：
   - 绝对杜绝空洞臆造与误导性假信息：严禁捏造具体售价、虚构买家评分、凭空编造 SKU 编码或伪造测试合格结论！
   - 所有关于市场价格区间、买家真实吐槽原声、工程认证标准（ASTM / IBC / ADA 等）与竞品对比的核心观点，必须尽可能紧随其后附带可点击验证的 Markdown 超链接，格式为：`[来源名称/页面](https://...)`。
   - 查不到时诚实标注：若某项具体参数在公开网络无法检索确认，严禁凭空臆测，必须明确标明 `【未找到公开源】` 或 `【公开数据无法验证】`，向用户披露不确定性，绝不提供看似真实实则误导的虚假信息！

8. 闭环验证：所有 P0 级设计改进必须能够追溯到明确的 VOC 痛点或竞品缺陷，并制定具体的 EVT/DVT/PVT 验证方法。
"""

# ==============================================================================
# 3. 各供应商最新模型字典映射表与高可用防 503 备选池
# ==============================================================================
PROVIDER_MODELS = {
    "Google Gemini": [
        "gemini-2.0-flash (经典高稳定极速版: 算力池最大，几乎永不过载)",
        "gemini-1.5-flash (长效高并发主力: 极少过载，推荐)",
        "gemini-2.5-flash (2026官方高智能极速版)",
        "gemini-3.6-flash (最新稳定高智能+超低延迟)",
        "gemini-3.8-flash (前沿旗舰极速版)",
        "gemini-3.5-flash (Agentic推荐: 复杂工作流专用)",
        "gemini-3.7-flash (高能效多模态)",
        "gemini-1.5-pro (长上下文与深度逻辑旗舰)",
        "gemini-2.5-pro (前沿深度推理旗舰)",
        "gemini-3.1-pro-preview (SOTA级超长上下文与深度逻辑)",
        "gemini-flash-latest (动态指向最新稳定版)"
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
    "Google Gemini": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash", "gemini-flash-latest"],
    "WorkBuddy (腾讯云 AI Agent)": ["deepseek-chat", "deepseek-reasoner", "hunyuan-pro", "gpt-4o"],
    "DeepSeek (深度求索)": ["deepseek-chat", "deepseek-reasoner"],
    "OpenAI (ChatGPT)": ["gpt-4o-mini", "gpt-4o", "o3-mini"],
    "Anthropic Claude": ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022", "claude-3-7-sonnet-20250219"]
}

def is_transient_error(err_str):
    """判断是否为临时性负载/限流错误"""
    transient_keywords = ["503", "overload", "unavailable", "server is busy", "502", "504", "rate limit", "temporarily", "429", "resource_exhausted", "capacity", "timeout"]
    return any(k in err_str.lower() for k in transient_keywords)

def is_model_not_found_error(err_str):
    """判断是否为模型不存在/无权限（应立即秒切下一个备选模型）"""
    not_found_keywords = ["not found", "404", "invalid argument", "unsupported model", "permission denied", "not supported for generatecontent", "does not exist"]
    return any(k in err_str.lower() for k in not_found_keywords)

# ==============================================================================
# 4. 辅助功能：带安全截断与数据清洗的实时搜索
# ==============================================================================
def live_web_search(query, max_results=3):
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get('title', '').strip()
                href = r.get('href', '').strip()
                body = r.get('body', '').strip()[:300]
                results.append(f"【来源: {title}】({href}):\n{body}")
        combined = "\n\n".join(results)
        return combined[:1500]
    except Exception:
        return ""

# ==============================================================================
# 5. 侧边栏：配置与干净无残留启动单
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

    if f"dynamic_models_{provider}" not in st.session_state:
        st.session_state[f"dynamic_models_{provider}"] = list(PROVIDER_MODELS[provider])

    current_models = list(st.session_state[f"dynamic_models_{provider}"])
    if "自定义模型名称 (手动输入...)" not in current_models:
        current_models.append("自定义模型名称 (手动输入...)")

    col_m1, col_m2 = st.columns((3, 1))
    with col_m1:
        selected_model_option = st.selectbox(
            f"选择模型 ({provider.split(' ')[0]} 专属模型)",
            options=current_models,
            index=0
        )
    with col_m2:
        if provider == "Google Gemini":
            if st.button("🔄 刷新", help="通过您的 API Key 实时查询 Google 官方所有最新可用模型并载入"):
                if not api_key:
                    st.warning("请先填入 Key")
                else:
                    try:
                        from google import genai
                        temp_client = genai.Client(api_key=api_key)
                        fetched = []
                        for m in temp_client.models.list():
                            m_id = m.name.replace("models/", "") if hasattr(m, "name") else str(m)
                            if "gemini" in m_id.lower():
                                fetched.append(m_id)
                        if fetched:
                            merged = sorted(list(set(fetched + [m.split(" ")[0] for m in PROVIDER_MODELS["Google Gemini"]])), reverse=True)
                            st.session_state[f"dynamic_models_{provider}"] = merged
                            st.success(f"已同步 {len(fetched)} 个官方模型！")
                            st.rerun()
                    except Exception as e:
                        st.error(f"同步失败: {str(e)[:30]}")
    
    if "自定义模型名称" in selected_model_option:
        default_custom = "gemini-2.0-flash" if "Gemini" in provider else ("deepseek-chat" if "WorkBuddy" in provider or "DeepSeek" in provider else "gpt-4o")
        model_name = st.text_input("请输入具体模型 ID:", value=default_custom)
    else:
        model_name = selected_model_option.split(" ")[0].strip()
        
    st.caption(f"当前生效模型: `{model_name}`")
    
    temperature = st.slider(
        "严谨度 (Temperature)", 
        min_value=0.0, 
        max_value=0.5, 
        value=0.1, 
        step=0.05, 
        help="建议保持在 0.1 左右以确保数据真实准确"
    )

    st.markdown("---")
    st.header("📋 V3.0 丰富版项目启动单")
    
    # 示例模板可选载入器（默认不加载，输入框完全留空）
    with st.expander("💡 快速填入示例产品模板 (可选)"):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("📦 载入【地板出风口 4x10】示例"):
                st.session_state["p_name"] = "Decorative Floor Register (美标装饰性地板出风口 4x10)"
                st.session_state["p_url"] = "https://www.homedepot.com/b/Heating-Venting-Cooling-HVAC-Supplies-Registers-Grilles/Floor-Register/N-5yc1vZc4ncZ1z0vj6i"
                st.session_state["p_size"] = "4x10 inches (标称风管开孔)"
                st.session_state["p_mat"] = "重型铸铝 (Cast Aluminum) / 哑光黑粉末喷涂 (Matte Black)"
                st.session_state["p_load"] = "承重 >= 300 lbs, 防卡安全孔隙 < 9.5 mm"
                st.session_state["p_price"] = "零售目标: $14.99 - $19.99 | 落地成本: <= $4.20"
                st.session_state["p_comp"] = "Decor Grates 4x10 Cast Aluminum; Accord Ventilation 4x10 Register"
                st.session_state["p_focus"] = "1. 重点深挖量错表面尺寸退货\n2. 重点考察细高跟卡死与安全防护\n3. 重点解决踩踏变形与机械松动"
                st.session_state["p_imgs"] = "- [出风口测量与结构部位对照图](https://drive.google.com/file/d/1xZLbD0u2HuxXqasLykMmyg9UjLAE--IV/view?usp=drivesdk)\n- [4x10美标地板出风口四叶草格栅设计对比总图](https://drive.google.com/file/d/1G2kMu310d7Dz9Yu8xEtJf7GwHPHxp3AB/view?usp=drivesdk)\n- [4个四叶草优化设计方案(现代畅销款)](https://drive.google.com/file/d/1swL8WVegxnRSBU3eEes4PiKDd7T17-84/view?usp=drivesdk)"
                st.rerun()
        with col_t2:
            if st.button("🧹 一键清空所有输入框"):
                for k in ["p_name", "p_url", "p_size", "p_mat", "p_load", "p_price", "p_comp", "p_focus", "p_imgs"]:
                    st.session_state[k] = ""
                st.rerun()

    channel_mode = st.selectbox(
        "1. 目标零售渠道 :red[* (必选)]",
        options=["The Home Depot (THD)", "Lowe's", "Dual-Channel (THD + Lowe's 跨渠道对标)"],
        index=0
    )
    
    project_type = st.selectbox(
        "2. 项目核心类型 :red[* (必选)]",
        options=["竞品差评归因与改良", "新品自主定义开发", "Listing 深度优化", "Buyer 选品提案", "成本结构重构", "规格升级"]
    )
    
    product_name = st.text_input(
        "3. 目标品名 (英文 + 中文) :red[* (必填)]", 
        value=st.session_state.get("p_name", ""), 
        placeholder="例如：3/4 in. Plastic Half Clamp with Nail 或 Floor Register"
    )
    product_url = st.text_input(
        "4. 目标产品官方链接 / SKU :red[* (必填)]", 
        value=st.session_state.get("p_url", ""), 
        placeholder="例如：The Home Depot / Lowe's 详情页链接或 Store SKU / Item #"
    )
    nominal_size = st.text_input(
        "5. 标称开孔/关键尺寸基准 :red[* (必填)]", 
        value=st.session_state.get("p_size", ""), 
        placeholder="例如：3/4 inch、4x10 inches 等管径或开孔基准"
    )
    material_and_finish = st.text_input(
        "6. 预定材质与表面处理 (选填)", 
        value=st.session_state.get("p_mat", ""), 
        placeholder="例如：耐冲击塑料、铸铝哑光黑喷粉、镀锌钢等"
    )
    load_and_safety = st.text_input(
        "7. 承重/受力与安全规范标准 (选填)", 
        value=st.session_state.get("p_load", ""), 
        placeholder="例如：抗压防裂、承重 >= 300 lbs、耐腐蚀无泄漏等"
    )
    
    mounting_type = st.selectbox(
        "8.1 产品安装部位 / 应用大类 :red[* (必选)]",
        options=[
            "厨卫/橱柜/台面/管道 (Kitchen, Bath & Plumbing)",
            "地面安装 (Floor)",
            "墙面/天花板安装 (Wall & Ceiling)",
            "门窗/出入口五金 (Doors & Hardware)",
            "户外/甲板/庭院 (Outdoor & Deck)",
            "独立放置/免安装 (Freestanding/Portable)",
            "自定义安装载体"
        ],
        index=0
    )

    substrate_map = {
        "厨卫/橱柜/台面/管道 (Kitchen, Bath & Plumbing)": [
            "PEX/铜管/PVC管", "木龙骨/立柱 (Wood Studs)", "水泥砂浆底座", "瓷砖地面/台面 (Tile)", "木质底板 (Subfloor)"
        ],
        "地面安装 (Floor)": [
            "实木地板 (Hardwood)", "锁扣地板 (LVP/SPC)", "瓷砖 (Tile)", "地毯 (Carpet)", "水泥地面 (Concrete)"
        ],
        "墙面/天花板安装 (Wall & Ceiling)": [
            "石膏板 (Drywall/Sheetrock)", "木龙骨 (Wood Studs)", "集成吊顶板 (Drop Ceiling Tile)", "砖石/水泥墙 (Masonry)"
        ]
    }

    current_options = substrate_map.get(mounting_type, ["常规硬质基体"])
    selected_substrates = st.multiselect(
        "8.2 目标安装介质/接触材质 :red[* (必选)]",
        options=current_options,
        default=current_options[:2] if len(current_options) >= 2 else current_options
    )
    
    target_price = st.text_input(
        "9. 目标零售价与成本线 (USD) (选填)", 
        value=st.session_state.get("p_price", ""), 
        placeholder="例如：零售 $4.99 - $7.99 | 落地成本 <= $1.20"
    )
    competitors = st.text_area(
        "10. 指定竞品对标链接/品牌型号 (选填)", 
        value=st.session_state.get("p_comp", ""), 
        placeholder="输入参考竞品的品牌型号或详情链接；若留空，系统将全网自动检索匹配竞品",
        height=80
    )
    focus_points = st.text_area(
        "11. 专项排他约束 / 核心关注痛点 (选填)", 
        value=st.session_state.get("p_focus", ""), 
        placeholder="输入希望重点深挖的买家差评痛点或改进方向；若留空，系统将进行全面深度调研",
        height=80
    )

    image_ref_urls = st.text_area(
        "12. 产品部位图与样品图链接库 (选填，仅在需要图文对照时填入)",
        value=st.session_state.get("p_imgs", ""),
        height=80,
        placeholder="粘贴产品部位图或样品的 Markdown 链接；若留空则不强制配图"
    )

    st.markdown("---")
    extra_live_data = st.text_area(
        "💡 实时数据补充仓 (选填，直接注入真实数据)",
        value="",
        placeholder="若有具体的商品参数卡片、官网截图文本或买家评论原文，可直接粘贴在此处，系统将强制以此作为事实基准！"
    )

# ==============================================================================
# 6. 底层通用调用接口 (开启 Google 搜索 Grounding，并自动提取真实核验超链接)
# ==============================================================================
def call_single_attempt(provider_name, api_key_val, model_id, final_prompt, base_url_val=""):
    if provider_name == "Google Gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key_val)
        
        # 核心防误导升级：开启 Google 官方 Search Grounding，直接抓取一手真实数据与可验证超链接
        config_args = {
            "system_instruction": SOP_SYSTEM_INSTRUCTION,
            "tools": [types.Tool(google_search=types.GoogleSearch())]
        }
        if "pro" in model_id.lower() or "flash" in model_id.lower():
            config_args["temperature"] = temperature
            
        try:
            config = types.GenerateContentConfig(**config_args)
            response = client.models.generate_content(
                model=model_id,
                contents=final_prompt,
                config=config
            )
        except Exception:
            # 容错降级：若特定极少数模型不支持 tools 则退回标准调用
            config_args.pop("tools", None)
            config = types.GenerateContentConfig(**config_args)
            response = client.models.generate_content(
                model=model_id,
                contents=final_prompt,
                config=config
            )

        res_text = response.text or ""

        # 智能提取 Google 官方检索到的真实来源超链接并挂载文末，供用户直接点击核验
        grounding_links = []
        try:
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                    gm = candidate.grounding_metadata
                    if hasattr(gm, "grounding_chunks") and gm.grounding_chunks:
                        for chunk in gm.grounding_chunks:
                            if hasattr(chunk, "web") and chunk.web:
                                t = getattr(chunk.web, "title", "") or "权威官方参考源"
                                u = getattr(chunk.web, "uri", "")
                                if u and u.startswith("http") and u not in [l[1] for l in grounding_links]:
                                    grounding_links.append((t, u))
        except Exception:
            pass

        if grounding_links:
            header_str = "\n\n---\n**🔗 Google 官方实时检索核验来源 (点击可直接验证):**\n"
            res_text += header_str
            for title, uri in grounding_links[:6]:
                res_text += f"- [{title}]({uri})\n"

        return res_text

    elif provider_name in ["WorkBuddy (腾讯云 AI Agent)", "OpenAI (ChatGPT)", "DeepSeek (深度求索)", "OpenAI 兼容中转 / OpenRouter / 自定义 API"]:
        import openai
        if provider_name == "WorkBuddy (腾讯云 AI Agent)":
            client = openai.OpenAI(api_key=api_key_val, base_url=base_url_val or "https://api.workbuddy.cn/v1", timeout=90.0)
        elif provider_name == "DeepSeek (深度求索)":
            client = openai.OpenAI(api_key=api_key_val, base_url="https://api.deepseek.com", timeout=90.0)
        elif provider_name == "OpenAI 兼容中转 / OpenRouter / 自定义 API":
            client = openai.OpenAI(api_key=api_key_val, base_url=base_url_val or "https://openrouter.ai/api/v1", timeout=90.0)
        else:
            client = openai.OpenAI(api_key=api_key_val, timeout=90.0)

        is_reasoner = any(k in model_id.lower() for k in ["o1", "o3", "reasoner"])
        if is_reasoner:
            messages = [
                {"role": "user", "content": f"【系统指导准则】\n{SOP_SYSTEM_INSTRUCTION}\n\n【当前分析任务】\n{final_prompt}"}
            ]
            call_args = {"model": model_id, "messages": messages}
        else:
            messages = [
                {"role": "system", "content": SOP_SYSTEM_INSTRUCTION},
                {"role": "user", "content": final_prompt}
            ]
            call_args = {"model": model_id, "messages": messages, "temperature": temperature}

        res = client.chat.completions.create(**call_args)
        return res.choices[0].message.content

    elif provider_name == "Anthropic Claude":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key_val, timeout=90.0)
        res = client.messages.create(
            model=model_id,
            system=SOP_SYSTEM_INSTRUCTION,
            max_tokens=8192,
            temperature=temperature,
            messages=[{"role": "user", "content": final_prompt}]
        )
        return res.content[0].text
    else:
        raise ValueError(f"未受支持的供应商: {provider_name}")

# ==============================================================================
# 7. 高鲁棒性执行器封装 (智能秒切备用、平滑退避、动态自清)
# ==============================================================================
def execute_stage(provider_name, api_key_val, model_id, stage_prompt, stage_name, search_query="", base_url_val=""):
    realtime_context = ""
    if search_query:
        with st.spinner(f"正在实时抓取一手网络数据: {search_query[:30]} ..."):
            fetched_data = live_web_search(search_query)
            if fetched_data:
                realtime_context = f"\n\n【最新互联网实时抓取证据库】:\n{fetched_data}\n"
    
    if extra_live_data.strip():
        realtime_context += f"\n\n【用户补充事实库】:\n{extra_live_data.strip()}\n"

    final_prompt = stage_prompt + realtime_context

    # 构建高可用候选模型梯队 (当前主选 -> 高可用保底模型)
    candidate_models = [model_id]
    if provider_name in FALLBACK_MODELS:
        for fb in FALLBACK_MODELS[provider_name]:
            if fb != model_id and fb not in candidate_models:
                candidate_models.append(fb)

    last_err = ""
    status_bar = st.empty()
    
    for current_model in candidate_models[:3]:
        # 每个模型最多重试 2 次，避免陷入漫长等待
        for attempt in range(1, 3):
            with st.spinner(f"⚡ 正在执行: {stage_name} (模型: `{current_model}`)..."):
                try:
                    result = call_single_attempt(provider_name, api_key_val, current_model, final_prompt, base_url_val)
                    status_bar.empty()  # 成功后立即清除临时状态提示
                    if current_model != model_id:
                        st.caption(f"💡 注：主模型遇波峰，此阶段已通过高可用备选模型 `{current_model}` 成功生成。")
                    return result
                except Exception as e:
                    last_err = str(e)
                    # 1. 若是模型名不存在或无权限，绝不浪费时间重试，直接秒切下一个模型
                    if is_model_not_found_error(last_err):
                        status_bar.info(f"🔄 模型 `{current_model}` 暂未开放或不可用，正在直接秒切备选模型...")
                        break
                    # 2. 若是 503/429 负载波动，进行平滑退避
                    elif is_transient_error(last_err):
                        wait_sec = attempt * 3
                        status_bar.info(f"⏳ `{current_model}` 遇到瞬时流量波峰，正在退避重试 ({attempt}/2，等待 {wait_sec}s)...")
                        time.sleep(wait_sec)
                    else:
                        status_bar.empty()
                        return f"❌ 阶段执行遇到异常: {last_err}"
        
        status_bar.info(f"🔄 模型 `{current_model}` 当前较拥挤，正在自动切至高可用备选模型...")
        time.sleep(1.0)

    status_bar.empty()
    return f"❌ 阶段执行失败：模型服务繁忙，请在下方点击【🔄 重新运行】即可重试。\n错误原因: {last_err}"

# 初始化会话状态 (Stage 1 至 Stage 6)
for i in range(1, 7):
    if f"stage{i}_res" not in st.session_state:
        st.session_state[f"stage{i}_res"] = ""

def build_prompts():
    context_header = f"""
【SOP V3.0 启动单输入参数】
- 目标渠道: {channel_mode}
- 项目类型: {project_type}
- 当前目标分析产品: 【{product_name}】
- 官方详情页链接 / 编码: {product_url}
- 标称开孔/尺寸基准: {nominal_size}
- 材质与表面处理: {material_and_finish}
- 承重与物理安全/规范: {load_and_safety}
- 安装部位与介质: 【安装部位: {mounting_type} | 介质载体: {', '.join(selected_substrates)}】
- 目标价格与成本线: {target_price}
- 指定对标竞品: {competitors}
- 核心关注痛点与约束: {focus_points}
- 可调用的产品部位与设计样品图库 (必须按需嵌入 Markdown 链接图文对照):
{image_ref_urls}

【最高隔离与防幻觉红线：100% 专属于当前产品】
你必须且仅能针对当前启动单输入的具体产品【{product_name}】展开分析！
1. 严禁混淆品类：严禁把其他历史产品的结构部件、竞品或痛点张冠李戴到【{product_name}】上！
2. 绝对真实可信：所有数据（价格、评分、评价数、SKU编码、关键尺寸、认证标准）必须基于事实检索，尽量提供可点击 Markdown 超链接 [来源页面](URL)！严禁臆造！
3. 若检索不到确切数据，严禁瞎编，必须明确标注【无法验证】或【未找到公开源】。
"""
    p1 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 1: 物理架构与规格基准库】（涵盖 Node 00, 00.5, 01, 02）：
【核心准则：通俗大白话 + 中英双语精准对照 + 强制附带可验证超链接 (拒绝误导假信息)】
- 【超链接强制核验】：给出的价格区间、评分、Item/SKU编码、测试标准，必须尽可能附带可点击的真实 Markdown 超链接 [来源页面](URL)！
- 【实事求是】：若某项参数（如壁厚、内径）在官方页面未公开，严禁瞎编，必须明确标注【无法验证】或【未找到公开源】！
1. 【00 & 00.5 项目章程与渠道界定】：用简单直白的大白话明确在 {channel_mode} 渠道下的业务目标与审核标准。
2. 【01 产品基础规格拆解库】：
   - 提取目标产品的最新真实参数（价格、评分、SKU/Item编号、质保、认证），结论先行。
   - 【尺寸大白话解耦 + 实体英文双语】：严禁使用晦涩官方腔与生硬机翻！结合当前【{product_name}】的实际物理形态，用大白话讲清楚尺寸基准（内外径/开孔/安装公差），告诉买家量哪里才不会买错退货。
   - 【必须嵌入实物测量与部位图】：若当前产品在图库中有匹配图示，必须嵌入对应 Markdown 图示链接。
   - 建立结构化【Product Specification Database】双语表格（包含公制mm与英制尺寸、公差与置信度）。
3. 【02 渠道产品定位】：分析在 {channel_mode} 货架上的生态位，用大白话讲清用户为什么买它。
所有关键名词统一使用【中文通俗名 (北美零售官方一手英文 Native Term)】格式。
"""
    p2 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 2: 场景矩阵、适配性与真实 VOC 挖掘】（涵盖 Node 03, 04, 05, 05.5）：
【核心准则：生活化场景大白话 + 中英双语真实买家原声吐槽 + 附带差评来源】
1. 【03 真实四维场景矩阵】：结合所选【安装部位: {mounting_type}】与【介质: {', '.join(selected_substrates)}】，用大白话讲清当前产品【{product_name}】在日常使用中的真实工况与受力环境。
2. 【04 适配性与安装干涉】：针对不同介质，讲透会不会松动、会不会脱落、会不会损坏载体。禁止使用 "Fits All"！
3. 【05 真实买家 VOC 深度挖掘】：必须引用该产品真实 1~5 星英文差评原声词并附带中文通俗翻译，尽量提供差评来源网页超链接，提炼核心痛点。
4. 【05.5 竞品 VOC 对标分析】：对比参考竞品，讲清哪些是全行业通病，哪些是该款特有缺陷。
"""
    p3 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 3: 根因归因、结构拆解与制造工艺】（涵盖 Node 06, 07, 07.5）：
【核心准则：结构拆解精准英文双语 + 部件图文对照 + 讲透为什么坏】
1. 【06 差评根因归因链 (Root Cause)】：建立链条：买家大白话抱怨 → 物理坏损表象 → 核心机械/材质根因。
2. 【07 物理结构拆解 (Teardown)】：
   - 针对当前产品【{product_name}】逐一拆解核心零配件，使用精准的实体地道英文双语标明。
   - 若图库中有匹配部件图，必须在文字后紧跟对应的部件图链接。
3. 【07.5 制造工艺与质量风险】：用通俗语言讲解其材质加工（如注塑、冲压、压铸、焊接等）容易出现缩水、开裂、生锈、公差失效的风险点。
"""
    p4 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 4: 商业数据库、机会排序与下一代产品定义】（涵盖 Node 08, 09, 09.5, 10, 11, 11.5, 12, 13, 14）：
【核心准则：地道商业与设计双语 + 方案对比 + 清晰定义下一代爆款】
1. 【08-09 竞品与规格数据库】：多竞品横向比对表（最新价格、评分、核心卖点，关键特性中英双语，附带真实竞品超链接）。
2. 【09.5 成本结构测算】：估算 BOM 材料、模具分摊、包装与海运落地成本 (Landed Cost)。
3. 【11-12 痛点排序与设计机会】：建立 `VOC 痛点 → 根因 → 机会 → 结构改良` 闭环。
4. 【13-14 下一代产品定义与方案推荐】：
   - 针对当前产品【{product_name}】定义改进型下一代爆款方案，若有样品图则嵌入对应链接。
   - 明确必须满足的硬指标 (Must-Have P0) 与体验升级 (Should-Have P1)。
"""
    p5 = f"""{context_header}
基于全部前期调研成果，请严格执行《SOP V3.0》的【Stage 5: 验证计划、渠道专属 Listing 与 20 问终极闭环】（涵盖 Node 15, 16, 17, 18）：
【核心准则：纯正北美电商英文 Listing + 小白一秒看懂的防买错指引】
1. 【15 EVT / DVT / PVT 工程测试计划】：关键受力测试、环境老化测试的标准与中英对照（必须引用 ASTM / IBC 官方标准全称）。
2. 【16 {channel_mode} 专属 Listing 策略】：
   - 【地道高转化英文 Title】：符合北美大零售平台搜索推荐算法的高转化词。
   - 【Native English Bullet Points】：地道 5 点卖点（英语原生文案 + 中文通俗对照）。
   - 【小白防买错指南 (Compatibility Guide)】：用最简单的大白话和地道英文教买家怎么选择与安装，彻底阻断退货。
3. 【17 终版产品定义书 (Final Definition)】：工程规格卡片（中英双语）。
4. 【18 终极闭环：解答 20 个产品开发核心决策问题】：逐一精确作答 20 个核心决策问题。
"""
    p6 = f"""{context_header}
基于 Stage 1 至 Stage 5 的全部深度调研成果，请执行 SOP 的【压轴 Stage 6: 汇报级终极决策总结看板 (Executive Summary Dashboard)】：
【核心目标】：严禁长篇大论！文字必须全部采用通俗易懂的大白话，关键部件与指标强制采用【中文通俗名 (北美行业地道英文 Native Term)】双语标注，把当前产品【{product_name}】的最重要部分精炼提取出来，形成一份【一页纸、精确可汇报、高管/总监一眼看透问题与决策】的高效报告看板。

请严格按照以下四大模块精炼输出：
1. 🚦【致命缺陷红绿灯诊断表 (Fatal Flaws Red/Yellow/Green)】：
   - 提取导致退货与差评的 Top 致命死穴（用 🔴 极高风险 / 🟡 中高风险 / 🟢 建议优化 标出）。
   - 每项必须列出：受损/缺陷部位（双语标注）、买家真实原声吐槽（中英双语，附带来源链接）、通俗工程解决措施、明确验证标准。
2. 📊【核心硬性工程红线指标速查表 (Critical Specs Baseline)】：
   - 提取最核心的物理与工程硬指标，包含大白话通俗说明与公制/英制双轨数值。
3. 🏆【产品选型与渠道落地决策 (Product Selection & GTM)】：
   - 给出推荐方案的定位、差异化优势与渠道定价建议。
4. 📋【下一步立即可执行行动清单 (Action Items)】：
   - 打样验证要点、包装图文防退货整改、首单采购建议。
"""
    return [p1, p2, p3, p4, p5, p6]

# ==============================================================================
# 8. 执行控制栏与流水线调用
# ==============================================================================
col_btn, col_clear, col_info = st.columns(3)
with col_btn:
    run_all_btn = st.button("🚀 启动 SOP V3.0 全流程分析 (实时准确模式)", type="primary", use_container_width=True)
with col_clear:
    if st.button("🧹 清空旧数据 (切换新产品)", use_container_width=True):
        for i in range(1, 7):
            st.session_state[f"stage{i}_res"] = ""
        st.session_state["analyzed_product_name"] = ""
        st.success("已彻底清空上一产品的所有历史数据！")
        st.rerun()
with col_info:
    if not api_key:
        st.info(f"💡 请先在左侧输入您的 {provider.split(' ')[0]} 凭证即可启动。")

# 检测品名变动提醒
if "analyzed_product_name" in st.session_state and st.session_state["analyzed_product_name"] and st.session_state["analyzed_product_name"] != product_name:
    st.warning(f"💡 **产品切换提醒**：左侧品名已变更为【{product_name}】，但下方仍保留着上一产品【{st.session_state['analyzed_product_name']}】的分析历史。点击上方【🚀 启动全流程分析】即可立即为新产品生成专属报告；或点击【🧹 清空旧数据】立即重置。")

if run_all_btn:
    if not api_key:
        st.error(f"启动失败：缺少 {provider.split(' ')[0]} API Key，请在左侧侧边栏配置。")
    elif not product_name.strip() or not nominal_size.strip() or not product_url.strip():
        st.error("启动失败：请填写所有标红【* (必填)】项（目标品名、尺寸基准、产品链接）。")
    else:
        # 启动新产品前，立即彻底清空上一产品的残留缓存
        for i in range(1, 7):
            st.session_state[f"stage{i}_res"] = ""
        st.session_state["analyzed_product_name"] = product_name
        
        prompts = build_prompts()
        stage_names = [
            "Stage 1 物理架构与规格库 (通俗白话+部位图)",
            "Stage 2 场景适配与 VOC 挖掘 (生活大白话)",
            "Stage 3 根因归因与结构制造 (图文拆解)",
            "Stage 4 机会矩阵与下一代定义 (样品对比图)",
            "Stage 5 验证计划与 Listing (防买错指南)",
            "Stage 6 汇报级终极决策总结看板 (一页纸汇报)"
        ]
        search_queries = [
            f"{product_name} Home Depot price specifications dimensions review",
            f"{product_name} reviews complaints problems leakage fail",
            f"{product_name} teardown broken cracked failure",
            f"{competitors} price rating comparison" if competitors.strip() else f"{product_name} top competitors",
            f"{product_name} installation manual test standard",
            f"{product_name} executive summary decision benchmark"
        ]
        
        for idx in range(6):
            st.session_state[f"stage{idx+1}_res"] = execute_stage(
                provider, api_key, model_name, prompts[idx], stage_names[idx], 
                search_query=search_queries[idx], base_url_val=custom_base_url
            )
            if idx < 5:
                time.sleep(2.5)  # 平滑缓冲避免 503/429
        st.success(f"🎉 【{product_name}】全流程深度研究已执行完毕！")

# ==============================================================================
# 9. 多标签页呈现、单步独立重试与报告导出
# ==============================================================================
if any(st.session_state[f"stage{i}_res"] for i in range(1, 7)):
    tab_sum, tab1, tab2, tab3, tab4, tab5, tab_full = st.tabs([
        "📊 Stage 6: 汇报级总结看板",
        "📐 Stage 1: 规格基准库 (大白话+部位图)",
        "🏡 Stage 2: 场景与真实 VOC",
        "🔬 Stage 3: 根因与结构拆解",
        "💡 Stage 4: 机会与下一代定义",
        "🎯 Stage 5: 验证计划与 Listing",
        "📄 完整报告总览与导出"
    ])
    
    prompts = build_prompts()
    
    def render_stage_tab(tab, stage_idx, stage_title, sq):
        with tab:
            st.markdown(st.session_state[f"stage{stage_idx}_res"])
            st.markdown("---")
            if st.button(f"🔄 实时重新检索并运行此阶段 ({stage_title})", key=f"retry_{stage_idx}"):
                st.session_state[f"stage{stage_idx}_res"] = execute_stage(
                    provider, api_key, model_name, prompts[stage_idx-1], stage_title, 
                    search_query=sq, base_url_val=custom_base_url
                )
                st.rerun()

    render_stage_tab(tab_sum, 6, "Stage 6 汇报级终极决策总结看板", f"{product_name} executive summary report")
    render_stage_tab(tab1, 1, "Stage 1 规格基准库 (通俗白话+部位图)", f"{product_name} Home Depot price specifications")
    render_stage_tab(tab2, 2, "Stage 2 场景与真实 VOC", f"{product_name} complaints problems review")
    render_stage_tab(tab3, 3, "Stage 3 根因与结构拆解", f"{product_name} complaints problems review")
    render_stage_tab(tab4, 4, "Stage 4 机会与下一代定义", f"{competitors} specs price" if competitors.strip() else f"{product_name} specs")
    render_stage_tab(tab5, 5, "Stage 5 验证计划与 Listing", f"{product_name} installation manual test standard")

    with tab_full:
        full_content = f"""# {product_name} - 北美大零售产品开发深度调研报告 (SOP V3.0)
- **目标渠道**: {channel_mode}
- **底层驱动引擎**: {provider} ({model_name})
- **项目类型**: {project_type}
- **生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **标称尺寸**: {nominal_size}
- **安装部位与介质**: {mounting_type} - {', '.join(selected_substrates)}
- **目标参考链接**: {product_url}

---
# 📊 【高管汇报级一页纸决策看板 (Executive Summary Dashboard)】
{st.session_state.stage6_res}

---
# 📚 深度调研详版报告
## 【Stage 1: 物理架构与规格基准库】
{st.session_state.stage1_res}

---
## 【Stage 2: 场景矩阵、适配性与真实 VOC 挖掘】
{st.session_state.stage2_res}

---
## 【Stage 3: 根因归因、结构拆解与制造工艺】
{st.session_state.stage3_res}

---
## 【Stage 4: 商业数据库、机会排序与下一代产品定义】
{st.session_state.stage4_res}

---
## 【Stage 5: 验证计划、渠道专属 Listing 与 20 问终极闭环】
{st.session_state.stage5_res}
"""
        st.markdown(full_content)
        st.download_button(
            label="📥 一键下载完整研究报告 (.md)",
            data=full_content,
            file_name=f"{channel_mode.split(' ')[0]}_SOP_V3_{nominal_size.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
