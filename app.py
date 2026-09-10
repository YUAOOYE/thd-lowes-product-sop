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
# 2. SOP V3.0 核心系统提示词
# ==============================================================================
SOP_SYSTEM_INSTRUCTION = """
你现在担任北美大零售建材产品开发项目经理、资深工业设计分析顾问与结构工程专家。
你必须严格执行《北美建材大零售产品开发与竞品研究 SOP V3.0》（涵盖 The Home Depot 与 Lowe's 标准）。

【核心原则与五大红线】
1. 绝对真实性：所有数据必须依据提供的最新检索事实进行提炼。严禁捏造虚假参数。
2. 动态数据必须包含：当前市场售价区间、实际评分、评价数量级、官方产品代码（如 Home Depot Internet # / Store SKU，Lowe's Item #）。
3. 尺寸严格解耦与通俗讲透：标称安装尺寸/管径 (Nominal / Cutout)、插入配合部尺寸 (Drop-in / Body)、外沿法兰盘/面板尺寸 (Faceplate / Flange) 必须彻底区分，同时提供英制与公制毫米 (mm)。

4. 【去官方化与说大白话红线（拒绝假大空与学术八股）】：
   - 彻底摒弃官方晦涩套话、机械术语与空洞长句（如“流体阻抗”、“微观物理干涉”、“三维尺寸解耦映射”等）。
   - 全程使用一线业务员、现场安装师傅或普通买家一秒能懂的“通俗大白话 / 人话”进行讲解。
   - 关键概念必须直白翻译：
     * “尺寸解耦” -> “量哪里别买错！地洞多大（Duct Opening）、屁股多大（Drop-in Box）、盖子多大（Faceplate）”。
     * “防卡鞋跟标准 (Heel-proof)” -> “细高跟鞋、宠物爪子不卡，钥匙发卡等小物件不掉”。
     * “集中承重 (Point Load)” -> “大胖子单脚踩上去不凹不弯、不踩断”。
     * “风门调节机构” -> “脚尖勾动开关风量的小拨扭，防踢断、防太松自动滑落”。
     * “有效通风率 (Free Area)” -> “通气孔镂空面积占比，太密吹不出风还吹哨子响，太疏人踩上去就变形”。
     * “耐腐蚀 (ASTM B117)” -> “拖地水、宠物尿液、热风冷凝水接触不掉漆、不生锈”。
   - 结论先行，杜绝冗长废话铺垫。

5. 【中英文双语对照与实体产品地道英文红线 (Product-Grounded Bilingual English)】：
   - 彻底拒绝生硬机翻、机械直译或脱离实体产品的抽象假英文：
     * 严禁用通用词直译：例如地板出风口严禁译为 "Air outlet" 或 "Ventilation cover"，必须使用北美建材零售标准品名 **Floor Register**（带风门）或 **Floor Grille**（不带风门纯格栅）。
     * 关键术语与部件必须统一格式：【中文通俗白话 (真实北美行业/实体产品一手英文术语 Native Trade & Retail Term)】。
   - 英文术语必须深度贴合“产品物理实体与北美大零售货架实际用语”：
     * 核心机械部位精准英文：
       - 表面格栅面板：Faceplate / Grille Flange Cover
       - 下沉配合风门箱体：Drop-in Damper Box / Rear Insert Collar
       - 风量控制百叶叶片：Louver Blades / Opposed Blade Damper (OBD)
       - 脚踩调节开关拨片：Actuator Lever / Foot-operated Air Volume Dial
       - 地面预留管口尺寸：Duct Opening / Floor Rough Cutout
       - 防卡鞋跟安全孔径：Heel-Proof Aperture Limit (< 9.5 mm / 3/8 in.)
       - 集中局部承重指标：Concentrated Walk-on Point Load (>= 300 lbs)
       - 低轮廓斜边倒角：Low-profile Beveled Transition Edge (< 3 mm)
       - 防异响缓冲密封垫：Anti-Vibration Rubber/Foam Gasket
       - 表面重型粉末喷涂：Heavy-duty Powder Coating (Matte Black 哑光黑, Oil Rubbed Bronze 复古青铜, Brushed Nickel 缎镍)
     * 买家真实痛点地道英文：
       - 量错表面买错退货：Ordered wrong size by measuring faceplate instead of duct
       - 高跟鞋卡陷摔跤：High heel caught in wide grille slots
       - 踩踏塌陷变形：Bent and warped after being walked on / Weak sheet metal
       - 调节拨片断裂或卡死：Stuck or snapped-off damper control lever
       - 管道气流吹口哨异响：Annoying whistling or rattling noise under high CFM
   - 商业与 Listing 英文：
     * 标题与卖点必须符合北美大零售平台搜索算法与真实买家搜索习惯（High-converting Search Terms），严禁中式英语语法。

6. 【图文对照红线（强制嵌入实际部位图与样品图链接）】：
   - 严禁干巴纯文字罗列。在解释产品物理结构、部位名称、测量方法、缺陷痛点以及下一代设计方案时，必须强制嵌入对应的【产品实际部位图、结构测量图或设计样品图】的 Markdown 链接（格式如：`[部位名称图示/样品图](链接URL)`）。
   - 优先从输入单提供的【产品部位图与样品图链接库】中调用对应链接。

7. 闭环验证：所有 P0 级设计改进必须能够追溯到明确的 VOC 痛点或竞品缺陷，并制定具体的 EVT/DVT/PVT 验证方法。
"""

# ==============================================================================
# 3. 各供应商最新模型字典映射表与自动防 503 备选池
# ==============================================================================
PROVIDER_MODELS = {
    "Google Gemini": [
        "gemini-3.6-flash (Google官方推荐: 最新稳定高智能+超低延迟)",
        "gemini-3.8-flash (2026最新前沿旗舰极速版)",
        "gemini-3.5-flash (Agentic推荐: 复杂工作流专用)",
        "gemini-3.7-flash (高能效多模态)",
        "gemini-3.1-pro-preview (SOTA级超长上下文与深度逻辑)",
        "gemini-flash-latest (动态指向最新稳定版)",
        "gemini-2.0-flash (经典兼容版本)"
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
    "Google Gemini": ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest"],
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
        default_custom = "gemini-3.6-flash" if "Gemini" in provider else ("deepseek-reasoner" if "WorkBuddy" in provider or "DeepSeek" in provider else "gpt-4o")
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
    
    channel_mode = st.selectbox(
        "1. 目标零售渠道*",
        options=["The Home Depot (THD)", "Lowe's", "Dual-Channel (THD + Lowe's 跨渠道对标)"],
        index=0
    )
    
    project_type = st.selectbox(
        "2. 项目核心类型*",
        options=["竞品差评归因与改良", "新品自主定义开发", "Listing 深度优化", "Buyer 选品提案", "成本结构重构", "规格升级"]
    )
    
    product_name = st.text_input("3. 目标品名 (英文 + 中文)*", value="Decorative Floor Register (美标装饰性地板出风口 4x10)")
    product_url = st.text_input("4. 目标产品官方链接 / SKU*", value="https://www.homedepot.com/b/Heating-Venting-Cooling-HVAC-Supplies-Registers-Grilles/Floor-Register/N-5yc1vZc4ncZ1z0vj6i")
    
    nominal_size = st.text_input("5. 标称开孔尺寸 (Duct Opening / Cutout)*", value="4x10 inches (标称风管开孔)")
    material_and_finish = st.text_input("6. 预定材质与表面处理", value="重型铸铝 (Cast Aluminum) / 哑光黑粉末喷涂 (Matte Black Powder Coat)")
    load_and_safety = st.text_input("7. 承重与物理安全/规范标准", value="承重 >= 300 lbs, 防卡鞋跟孔隙 < 9.5 mm (Heel-proof)")
    
    mounting_type = st.selectbox(
        "8.1 产品安装部位 / 应用大类*",
        options=[
            "地面安装 (Floor)",
            "厨卫/橱柜/台面/管道 (Kitchen, Bath & Plumbing)",
            "墙面/天花板安装 (Wall & Ceiling)",
            "门窗/出入口五金 (Doors & Hardware)",
            "户外/甲板/庭院 (Outdoor & Deck)",
            "独立放置/免安装 (Freestanding/Portable)",
            "自定义安装载体"
        ],
        index=0
    )

    substrate_map = {
        "地面安装 (Floor)": [
            "实木地板 (Hardwood)", "锁扣地板 (LVP/SPC)", "瓷砖 (Tile)", "地毯 (Carpet)", "水泥地面 (Concrete)"
        ],
        "厨卫/橱柜/台面/管道 (Kitchen, Bath & Plumbing)": [
            "PVC/ABS 排水管", "铸铁排水管 (Cast Iron)", "瓷砖地面 (Tile)", "木质底板 (Subfloor)"
        ],
        "墙面/天花板安装 (Wall & Ceiling)": [
            "石膏板 (Drywall/Sheetrock)", "木龙骨 (Wood Studs)", "集成吊顶板 (Drop Ceiling Tile)"
        ]
    }

    current_options = substrate_map.get(mounting_type, ["实木地板 (Hardwood)", "锁扣地板 (LVP/SPC)"])
    selected_substrates = st.multiselect(
        "8.2 目标安装介质/接触材质*",
        options=current_options,
        default=current_options[:2] if len(current_options) >= 2 else current_options
    )
    
    target_price = st.text_input("9. 目标零售价与成本线 (USD)", value="零售目标: $14.99 - $19.99 | 落地成本: ≤ $4.20")
    competitors = st.text_area("10. 指定竞品对标链接/品牌型号", value="Decor Grates 4x10 Cast Aluminum; Accord Ventilation 4x10 Register")
    focus_points = st.text_area("11. 专项排他约束 / 核心关注痛点", value="1. 重点深挖买家因量错表面尺寸导致的退货\n2. 重点考察细高跟卡死与小孩手指安全\n3. 重点解决踩踏变形与开关拨片太松自动滑落问题")

    default_image_refs = """- [出风口测量与结构部位对照图](https://drive.google.com/file/d/1xZLbD0u2HuxXqasLykMmyg9UjLAE--IV/view?usp=drivesdk) (风洞口测量、下沉风门箱体、可调百叶拨片、生锈松动痛点)
- [4x10美标地板出风口四叶草格栅设计对比总图](https://drive.google.com/file/d/1G2kMu310d7Dz9Yu8xEtJf7GwHPHxp3AB/view?usp=drivesdk) (原版6叶草基准 vs 推荐4叶草黄金比例 vs 3叶草大徽章款)
- [4个四叶草优化设计方案(现代畅销款)](https://drive.google.com/file/d/1swL8WVegxnRSBU3eEes4PiKDd7T17-84/view?usp=drivesdk) (通风率64.85%，防卡鞋跟合格，美标推荐爆款)
- [3个四叶草优化设计方案(经典大徽章款)](https://drive.google.com/file/d/1_dZjToDqAuaeW5DV6T-xuZBY0OLpIO9i/view?usp=drivesdk) (豪华大徽章，通风率71.5%，高端大宅款)
- [现代几何CAD概念设计图](https://drive.google.com/file/d/1LxhNMvv8VXUO_-RYKGLXVG81AlMtEUNZ/view?usp=drivesdk) (菱形编织纹、V型人字纹与包豪斯线条设计)
- [4x10哑光黑美标地板出风口设计概念图](https://drive.google.com/file/d/1CLO5J8bLdjDQ28IC-BDULo_j6up7qIlL/view?usp=drivesdk)"""

    image_ref_urls = st.text_area(
        "12. 产品部位图与样品图链接库 (自动图文对照)*",
        value=default_image_refs,
        height=140,
        help="系统将在分析专业术语、结构部位、尺寸测量及方案选型时强制嵌入对应图示链接"
    )

    st.markdown("---")
    extra_live_data = st.text_area(
        "💡 实时数据补充仓 (选填，直接注入真实数据)",
        value="",
        placeholder="若有具体的商品参数卡片、官网截图文本或买家评论原文，可直接粘贴在此处，系统将强制以此作为事实基准！"
    )

# ==============================================================================
# 6. 底层通用调用接口
# ==============================================================================
def call_single_attempt(provider_name, api_key_val, model_id, final_prompt, base_url_val=""):
    if provider_name == "Google Gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key_val)
        config = types.GenerateContentConfig(
            system_instruction=SOP_SYSTEM_INSTRUCTION,
            temperature=temperature
        )
        resp = client.models.generate_content(
            model=model_id,
            contents=final_prompt,
            config=config
        )
        return resp.text

    elif provider_name in ["WorkBuddy (腾讯云 AI Agent)", "DeepSeek (深度求索)", "OpenAI (ChatGPT)", "OpenAI 兼容中转 / OpenRouter / 自定义 API"]:
        from openai import OpenAI
        target_base_url = base_url_val or ("https://api.deepseek.com" if "DeepSeek" in provider_name else None)
        client = OpenAI(api_key=api_key_val, base_url=target_base_url)
        resp = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SOP_SYSTEM_INSTRUCTION},
                {"role": "user", "content": final_prompt}
            ],
            temperature=temperature
        )
        return resp.choices[0].message.content

    elif provider_name == "Anthropic Claude":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key_val)
        resp = client.messages.create(
            model=model_id,
            max_tokens=4096,
            system=SOP_SYSTEM_INSTRUCTION,
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            temperature=temperature
        )
        return resp.content[0].text
    else:
        raise ValueError(f"未受支持的供应商: {provider_name}")

# ==============================================================================
# 7. 执行器封装
# ==============================================================================
def execute_stage(provider_name, api_key_val, model_id, stage_prompt, stage_name, search_query="", base_url_val=""):
    web_context = ""
    if search_query:
        with st.spinner(f"🔍 正在从全网检索真实工程与市场事实: `{search_query[:35]}...`"):
            web_context = live_web_search(search_query)

    supp_part = f"\n【用户注入真实事实仓】:\n{extra_live_data}\n" if extra_live_data.strip() else ""
    web_part = f"\n【全网一手实时检索证据（以此为准）】:\n{web_context}\n" if web_context else ""
    final_prompt = f"{stage_prompt}\n{supp_part}\n{web_part}"

    candidates = [model_id]
    for fb in FALLBACK_MODELS.get(provider_name, []):
        if fb not in candidates:
            candidates.append(fb)

    last_err = ""
    for current_model in candidates:
        for attempt in range(3):
            try:
                with st.spinner(f"⚡ 正在深度分析: {stage_name} (运行模型: `{current_model}`)..."):
                    return call_single_attempt(provider_name, api_key_val, current_model, final_prompt, base_url_val=base_url_val)
            except Exception as e:
                err_msg = str(e)
                last_err = err_msg
                if is_transient_error(err_msg):
                    wait_sec = (attempt + 1) * 2
                    st.warning(f"⚠️ `{current_model}` 遭遇负载波动，正在自动重试 ({attempt+1}/3，等待 {wait_sec}s)...")
                    time.sleep(wait_sec)
                else:
                    return f"❌ 阶段执行失败: {err_msg}"
        
        st.warning(f"⚠️ 模型 `{current_model}` 目前过载，正在自动切换至备选模型继续执行...")
        time.sleep(2)

    return f"❌ 阶段执行失败（服务器持续过载）：供应商 [{provider_name}] 繁忙，请重试。\n详情: {last_err}"

# 初始化会话状态 (Stage 1 至 Stage 6)
for i in range(1, 7):
    if f"stage{i}_res" not in st.session_state:
        st.session_state[f"stage{i}_res"] = ""

def build_prompts():
    context_header = f"""
【SOP V3.0 启动单输入参数】
- 目标渠道: {channel_mode}
- 项目类型: {project_type}
- 产品名称: {product_name}
- 官方详情页链接 / 编码: {product_url}
- 标称开孔/切口尺寸: {nominal_size}
- 材质与表面处理: {material_and_finish}
- 承重与物理安全: {load_and_safety}
- 安装部位与介质: 【安装部位: {mounting_type} | 介质载体: {', '.join(selected_substrates)}】
- 目标价格与成本线: {target_price}
- 指定对标竞品: {competitors}
- 核心关注痛点与约束: {focus_points}
- 可调用的产品部位与设计样品图库 (必须按需嵌入 Markdown 链接图文对照):
{image_ref_urls}
"""
    p1 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 1: 物理架构与规格基准库】（涵盖 Node 00, 00.5, 01, 02）：
【核心准则：全用通俗大白话 + 中英双语精准对照 + 强制部位图文对照】
1. 【00 & 00.5 项目章程与渠道界定】：用简单直白的大白话明确在 {channel_mode} 渠道下的业务目标与审核标准。
2. 【01 产品基础规格拆解库】：
   - 提取目标产品的最新真实参数（价格、评分、SKU/Item编号、质保、认证），结论先行。
   - 【尺寸大白话解耦 + 实体英文双语】：严禁使用晦涩官方腔与生硬机翻！必须用大白话讲清楚：
     * 地洞多大 (Duct Opening / Floor Cutout)
     * 屁股多大 (Drop-in Damper Box / Rear Collar)
     * 盖子多大 (Faceplate / Grille Flange)
     告诉买家量哪里才不会买错退货（【特别提醒】：千万别量表面盖板，只量地洞）。
   - 【强制嵌入实物测量与部位图】：在讲解尺寸基准与对应结构部位时，必须嵌入【产品部位与设计样品图库】中的对应图示链接（如 [出风口测量与结构部位对照图](...)）。
   - 建立结构化【Product Specification Database】双语表格（包含公制mm与英制尺寸、公差与置信度）。
3. 【02 渠道产品定位】：分析在 {channel_mode} 货架上的生态位，用大白话讲清用户为什么买它。
所有关键名词统一使用【中文通俗名 (北美零售官方一手英文 Native Term)】格式。
"""
    p2 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 2: 场景矩阵、适配性与真实 VOC 挖掘】（涵盖 Node 03, 04, 05, 05.5）：
【核心准则：生活化场景大白话 + 中英双语真实买家原声吐槽】
1. 【03 真实四维场景矩阵】：结合所选【安装部位: {mounting_type}】与【介质: {', '.join(selected_substrates)}】，地材与介质名称采用双语（实木地板 Hardwood、锁扣地板 LVP/SPC、瓷砖 Tile、地毯 Carpet），用大白话讲清在日常生活中（如扫地机器人通过、小孩光脚跑过、拖地带水）的实际工况与摩擦。
2. 【04 适配性与安装干涉】：针对不同地面或管道介质，讲透会不会绊脚、会不会刮伤地板、会不会晃荡异响 (Rattling)。禁止使用 "Fits All"！
3. 【05 真实买家 VOC 深度挖掘】：必须引用买家真实 1~5 星英文差评原声词（如 doesn't stay open, rusted, cheap flimsy metal, whistling noise）并附带中文通俗翻译，提炼出让买家愤怒的核心痛点。
4. 【05.5 竞品 VOC 对标分析】：对比参考竞品（{competitors}），讲清哪些是全行业通病，哪些是该款特有缺陷。
"""
    p3 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 3: 根因归因、结构拆解与制造工艺】（涵盖 Node 06, 07, 07.5）：
【核心准则：结构拆解精准英文双语 + 强制部件图文对照 + 讲透为什么坏】
1. 【06 差评根因归因链 (Root Cause)】：建立链条：买家大白话抱怨 → 物理坏损表象 → 核心机械/材质根因。
2. 【07 物理结构拆解 (Teardown)】：
   - 拆解核心零配件，必须使用精准的产品实体地道英文双语标明：
     * 表面面板 (Faceplate / Flange)
     * 下沉风门箱体 (Drop-in Damper Box)
     * 风量百叶叶片 (Louver Blades / Opposed Blades)
     * 开关调节拨片 (Actuator Lever / Foot Wheel)
     * 紧固弹簧/静音垫 (Tension Springs / Anti-Vibration Gasket)
   - 【强制图文对照】：涉及每一个关键零配件与缺陷部位时，必须在文字后紧跟对应的部件图或样品图链接（如 [出风口可调百叶实物图](...)、[老旧出风口生锈磨损图](...) 等）。
3. 【07.5 制造工艺与质量风险】：用通俗语言讲解压铸 (Die Casting)、冲压 (Stamping)、静电喷粉 (Powder Coating) 与容易出现缩水、积粉、掉漆、卡死的风险点。
"""
    p4 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 4: 商业数据库、机会排序与下一代产品定义】（涵盖 Node 08, 09, 09.5, 10, 11, 11.5, 12, 13, 14）：
【核心准则：地道商业与设计双语 + 方案对比图文对照 + 清晰定义下一代爆款】
1. 【08-09 竞品与规格数据库】：多竞品横向比对表（最新价格、评分、核心卖点，关键特性中英双语）。
2. 【09.5 成本结构测算】：估算 BOM 材料、模具分摊、包装与海运落地成本 (Landed Cost)。
3. 【11-12 痛点排序与设计机会】：建立 `VOC 痛点 → 根因 → 机会 → 结构改良` 闭环。
4. 【13-14 下一代产品定义与方案推荐】：
   - 【强制样品图对比】：在提出花纹方案与下一代定义时，必须嵌入【产品部位与设计样品图库】中的设计样品图（如 [4x10美标地板出风口四叶草格栅设计对比总图](...)、[4个四叶草优化设计方案(现代畅销款)](...)、[3个四叶草优化设计方案(经典大徽章款)](...) 等）。
   - 方案名称必须地道专业：如现代畅销款 (Modern Geometric Quatrefoil)、豪华大徽章款 (Luxury Tripartite Medallion)。
   - 明确必须满足的硬指标：防卡鞋跟 (Heel-proof < 9.5mm)、承重 (Concentrated Load >= 300 lbs)、有效通风率 (Free Area 60%-72%)。
"""
    p5 = f"""{context_header}
基于全部前期调研成果，请严格执行《SOP V3.0》的【Stage 5: 验证计划、渠道专属 Listing 与 20 问终极闭环】（涵盖 Node 15, 16, 17, 18）：
【核心准则：纯正北美电商英文 Listing + 小白一秒看懂的防买错指引】
1. 【15 EVT / DVT / PVT 工程测试计划】：承重测试、耐腐蚀盐雾测试 (ASTM B117)、开关拨片往复耐久测试的标准与中英对照。
2. 【16 {channel_mode} 专属 Listing 策略】：
   - 【地道高转化英文 Title】：符合北美大零售平台搜索推荐算法（如包含 heavy-duty cast aluminum, floor register, 4x10, matte black, heel-proof, walk-on 等高转化词）。
   - 【Native English Bullet Points】：地道 5 点卖点（英语原生文案 + 中文通俗对照）。
   - 【小白防买错指南 (Compatibility Guide)】：用最简单的大白话和地道英文教买家怎么量尺寸，彻底阻断退货。
3. 【17 终版产品定义书 (Final Definition)】：工程规格卡片（中英双语）。
4. 【18 终极闭环：解答 20 个产品开发核心决策问题】：逐一精确作答 20 个核心决策问题。
"""
    p6 = f"""{context_header}
基于 Stage 1 至 Stage 5 的全部深度调研成果，请执行 SOP 的【压轴 Stage 6: 汇报级终极决策总结看板 (Executive Summary Dashboard)】：
【核心目标】：严禁长篇大论！文字必须全部采用通俗易懂的大白话，关键部件与指标强制采用【中文通俗名 (北美行业地道英文 Native Term)】双语标注，把全部调研内容的最重要部分精炼提取出来，形成一份【一页纸、精确可汇报、高管/总监一眼看透问题与决策】的高效报告看板。

请严格按照以下四大模块精炼输出：
1. 🚦【致命缺陷红绿灯诊断表 (Fatal Flaws Red/Yellow/Green)】：
   - 提取导致退货与差评的 Top 4 致命死穴（用 🔴 极高风险 / 🟡 中高风险 / 🟢 建议优化 标出）。
   - 每项必须列出：受损/缺陷部位（双语标注，必须附带部位图链接）、买家真实原声吐槽（中英双语）、通俗工程解决措施、明确验证标准。
2. 📊【核心硬性工程红线指标速查表 (Critical Specs Baseline)】：
   - 提取最核心的物理与工程硬指标：开孔尺寸 (Duct Opening)、下沉配合尺寸 (Drop-in Box)、表面盖板尺寸 (Faceplate)、承重安全线 (Point Load)、防卡安全孔径 (Heel-proof)、通风率达标线 (Free Area)、表面防腐指标 (Salt Spray ASTM B117)。
   - 必须包含大白话通俗说明与公制/英制双轨数值。
3. 🏆【产品选型与渠道落地决策 (Product Selection & GTM)】：
   - 主力首发款（大众走量）：推荐哪个具体设计方案（双语命名，必须引用对应样品图链接），说明定位、通风率与成本优势。
   - 高端溢价款（利润款）：推荐哪个设计方案（双语命名，必须引用对应样品图链接），说明定位与溢价卖点。
4. 📋【下一步立即可执行行动清单 (Action Items)】：
   - 结构打样验证要点（验证什么、怎么测）。
   - 包装与说明书整改建议（如何用图文彻底阻断“买错尺寸退货”）。
   - 首单采购与上线时间节点建议。
"""
    return [p1, p2, p3, p4, p5, p6]

# ==============================================================================
# 8. 执行控制栏与流水线调用
# ==============================================================================
col_btn, col_info = st.columns(2)
with col_btn:
    run_all_btn = st.button("🚀 启动 SOP V3.0 全流程分析 (实时准确模式)", type="primary", use_container_width=True)
with col_info:
    if not api_key:
        st.info(f"💡 请先在左侧输入您的 {provider.split(' ')[0]} 凭证即可启动。")

if run_all_btn:
    if not api_key:
        st.error(f"启动失败：缺少 {provider.split(' ')[0]} API Key，请在左侧侧边栏配置。")
    elif not product_name or not nominal_size or not product_url:
        st.error("启动失败：启动单中的品名、开孔尺寸、产品链接为必填项。")
    else:
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
            f"{competitors} price rating comparison",
            f"{product_name} installation manual test standard",
            f"{product_name} executive summary decision benchmark"
        ]
        
        for idx in range(6):
            st.session_state[f"stage{idx+1}_res"] = execute_stage(
                provider, api_key, model_name, prompts[idx], stage_names[idx], 
                search_query=search_queries[idx], base_url_val=custom_base_url
            )
            if idx < 5:
                time.sleep(1)
        st.success("🎉 《北美建材大零售产品开发 SOP V3.0》全流程深度研究已执行完毕！")

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
    render_stage_tab(tab4, 4, "Stage 4 机会与下一代定义", f"{competitors} specs price")
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
