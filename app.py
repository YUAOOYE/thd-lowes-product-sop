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
st.markdown('<div class="sub-header">多模型引擎联动 (Gemini / WorkBuddy / OpenAI / Claude / DeepSeek) | 实时网络证据闭环 | 结构拆解与制造工艺 | 动态安装载体适配</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. SOP V3.0 核心系统提示词
# ==============================================================================
SOP_SYSTEM_INSTRUCTION = """
你现在担任北美大零售建材产品开发项目经理、资深工业设计分析顾问与结构工程专家。
你必须严格执行《北美建材大零售产品开发与竞品研究 SOP V3.0》（涵盖 The Home Depot 与 Lowe's 标准）。

【核心原则与证据红线】
1. 绝对真实性：所有数据必须依据提供的最新检索事实进行提炼。严禁捏造虚假参数。
2. 动态数据必须包含：当前市场售价区间、实际评分、评价数量级、官方产品代码（如 Home Depot Internet # / Store SKU，Lowe's Item #）。
3. 尺寸严格解耦：标称安装尺寸/管径 (Nominal / Cutout)、插入配合部尺寸 (Drop-in / Body)、外沿法兰盘/面板尺寸 (Faceplate / Flange) 必须彻底区分，同时提供英制与公制毫米 (mm)。
4. 真实 VOC 证据：Review 引用必须基于真实买家痛点（如密封老化漏水、塑料断裂、管壁锈蚀贴合不良），严禁编造空洞虚词。
5. 闭环验证：所有 P0 级设计改进必须能够追溯到明确的 VOC 痛点或竞品缺陷，并制定具体的 EVT/DVT/PVT 验证方法。
"""

# ==============================================================================
# 3. 各供应商最新模型字典映射表 (包含 WorkBuddy)
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

# ==============================================================================
# 4. 辅助功能：外置实时搜索（全平台模型共享一手实时网络证据）
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
# 5. 侧边栏：多供应商引擎联动配置与超丰富项目启动单
# ==============================================================================
with st.sidebar:
    st.header("⚙️ 多模型引擎配置")
    
    # 1. 供应商选择
    provider = st.selectbox(
        "选择 API 供应商*",
        options=list(PROVIDER_MODELS.keys()),
        index=0
    )
    
    # 根据不同供应商自动匹配 Secret Key 默认值
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
    
    # 自定义 Base URL (若选中 WorkBuddy、兼容端或 DeepSeek)
    custom_base_url = ""
    if provider == "WorkBuddy (腾讯云 AI Agent)":
        custom_base_url = st.text_input("WorkBuddy API Base URL*", value="https://api.workbuddy.cn/v1", help="支持腾讯云 WorkBuddy / CodeBuddy 官方 Token Plan 或本地网关地址")
    elif provider == "OpenAI 兼容中转 / OpenRouter / 自定义 API":
        custom_base_url = st.text_input("自定义 API Base URL*", value="https://openrouter.ai/api/v1", help="支持中转接口如 OpenRouter、OneAPI、SiliconFlow 等")
    elif provider == "DeepSeek (深度求索)":
        custom_base_url = "https://api.deepseek.com"

    # 2. 动态联动：根据选定供应商展示对应的最新模型列表
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
    
    product_name = st.text_input("3. 目标品名 (英文 + 中文)*", value="Twist-N-Set 3 in. ABS Open Toilet Flange (马桶法兰)")
    product_url = st.text_input("4. 目标产品官方链接 / SKU*", value="https://www.homedepot.com/p/Everbilt-Twist-N-Set-3-in-ABS-Open-Toilet-Flange-43542/100062260")
    
    nominal_size = st.text_input("5. 标称开孔尺寸 (Duct Opening / Cutout)*", value="3 inch (标称管径)")
    material_and_finish = st.text_input("6. 预定材质与表面处理", value="ABS 工程塑料 / 橡胶密封圈 (EPDM)")
    load_and_safety = st.text_input("7. 承重与物理安全/规范标准", value="UPC / cUPC 认证, 耐腐蚀无泄漏")
    
    # 动态联动的安装部位与介质
    mounting_type = st.selectbox(
        "8.1 产品安装部位 / 应用大类*",
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
            "PVC/ABS 排水管", "铸铁排水管 (Cast Iron)", "瓷砖地面 (Tile)", "水泥砂浆底座", "木质底板 (Subfloor)"
        ],
        "地面安装 (Floor)": [
            "实木地板 (Hardwood)", "锁扣地板 (LVP/SPC)", "瓷砖 (Tile)", "地毯 (Carpet)", "水泥地面 (Concrete)"
        ],
        "墙面/天花板安装 (Wall & Ceiling)": [
            "石膏板 (Drywall/Sheetrock)", "木龙骨 (Wood Studs)", "集成吊顶板 (Drop Ceiling Tile)", "砖石/水泥墙 (Masonry)"
        ],
        "门窗/出入口五金 (Doors & Hardware)": [
            "实木门 (Solid Wood)", "空心木门 (Hollow Core)", "金属防盗门 (Metal)", "玻纤门 (Fiberglass)"
        ],
        "户外/甲板/庭院 (Outdoor & Deck)": [
            "防腐木 (Treated Lumber)", "复合木塑板 (Composite/Trex)", "混凝土基座 (Concrete)", "外墙挂板 (Siding)"
        ],
        "独立放置/免安装 (Freestanding/Portable)": [
            "室内常规硬质台面/桌面", "地毯/地板自由摆放"
        ]
    }

    if mounting_type == "自定义安装载体":
        custom_sub = st.text_input("请输入具体的安装介质/载体材质:", value="特殊管道与地面基座")
        selected_substrates = [custom_sub]
    else:
        current_options = substrate_map.get(mounting_type, ["常规硬质基体"])
        selected_substrates = st.multiselect(
            "8.2 目标安装介质/接触材质*",
            options=current_options,
            default=current_options[:2] if len(current_options) >= 2 else current_options
        )
    
    target_price = st.text_input("9. 目标零售价与成本线 (USD)", value="零售目标: $14.99 - $18.99 | 落地成本: ≤ $3.50")
    competitors = st.text_area("10. 指定竞品对标链接/品牌型号", value="Oatey 43542 Twist-N-Set; Sioux Chief 3-inch Flange")
    focus_points = st.text_area("11. 专项排他约束 / 核心关注痛点", value="1. 重点深挖橡胶膨胀密封圈老化漏水、塑料法兰盘拧紧受力破裂、与铸铁旧管内壁锈蚀接触不紧密等差评\n2. 必须具备防异味反溢机制")
    
    st.markdown("---")
    extra_live_data = st.text_area(
        "💡 实时数据补充仓 (选填，直接注入真实数据)",
        value="",
        placeholder="若有具体的商品参数卡片、官网截图文本或买家评论原文，可直接粘贴在此处，系统将强制以此作为事实基准！"
    )

# ==============================================================================
# 6. 通用多模型调用执行器 (统一分发)
# ==============================================================================
def execute_stage(provider_name, api_key_val, model_id, stage_prompt, stage_name, search_query="", base_url_val=""):
    realtime_context = ""
    if search_query:
        with st.spinner(f"正在实时抓取一手网络数据: {search_query} ..."):
            fetched_data = live_web_search(search_query)
            if fetched_data:
                realtime_context = f"\n\n【最新互联网实时抓取证据库】:\n{fetched_data}\n"
    
    if extra_live_data.strip():
        realtime_context += f"\n\n【用户手动补充的真实事实库】:\n{extra_live_data.strip()}\n"

    final_prompt = stage_prompt + realtime_context

    with st.spinner(f"[{provider_name.split(' ')[0]} | {model_id}] 正在深度执行: {stage_name} ..."):
        try:
            # 模式 A: Google Gemini
            if provider_name == "Google Gemini":
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key_val)
                config = types.GenerateContentConfig(
                    system_instruction=SOP_SYSTEM_INSTRUCTION,
                    temperature=temperature
                )
                response = client.models.generate_content(
                    model=model_id,
                    contents=final_prompt,
                    config=config
                )
                return response.text

            # 模式 B: WorkBuddy / OpenAI / DeepSeek / 兼容中转
            elif provider_name in ["WorkBuddy (腾讯云 AI Agent)", "OpenAI (ChatGPT)", "DeepSeek (深度求索)", "OpenAI 兼容中转 / OpenRouter / 自定义 API"]:
                import openai
                if provider_name == "WorkBuddy (腾讯云 AI Agent)":
                    client = openai.OpenAI(api_key=api_key_val, base_url=base_url_val or "https://api.workbuddy.cn/v1")
                elif provider_name == "DeepSeek (深度求索)":
                    client = openai.OpenAI(api_key=api_key_val, base_url="https://api.deepseek.com")
                elif provider_name == "OpenAI 兼容中转 / OpenRouter / 自定义 API":
                    client = openai.OpenAI(api_key=api_key_val, base_url=base_url_val or "https://openrouter.ai/api/v1")
                else:
                    client = openai.OpenAI(api_key=api_key_val)

                messages = [
                    {"role": "system", "content": SOP_SYSTEM_INSTRUCTION},
                    {"role": "user", "content": final_prompt}
                ]
                call_args = {"model": model_id, "messages": messages}
                if not any(k in model_id.lower() for k in ["o1", "o3"]):
                    call_args["temperature"] = temperature

                res = client.chat.completions.create(**call_args)
                return res.choices[0].message.content

            # 模式 C: Anthropic Claude
            elif provider_name == "Anthropic Claude":
                import anthropic
                client = anthropic.Anthropic(api_key=api_key_val)
                res = client.messages.create(
                    model=model_id,
                    system=SOP_SYSTEM_INSTRUCTION,
                    max_tokens=8192,
                    temperature=temperature,
                    messages=[{"role": "user", "content": final_prompt}]
                )
                return res.content[0].text

        except Exception as e:
            return f"❌ 阶段执行失败: {str(e)}"

# 初始化会话状态
for i in range(1, 6):
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
"""
    p1 = f"""{context_header}
请严格执行《SOP V3.0》的【Stage 1: 物理架构与规格基准库】（涵盖 Node 00, 00.5, 01, 02）：
1. 【00 & 00.5 项目章程与渠道界定】：明确在 {channel_mode} 渠道下的业务目标、核心技术问题、非目标边界与审核标准。
2. 【01 产品基础规格拆解库】：
   - 提取目标产品的最新真实参数（市场零售价格区间、评分与评价量级、官方SKU/Item编号、质保期、标准认证如UPC/cUPC/ASTM）。
   - 强制三维尺寸解耦：标称安装尺寸/管径、插入配合部外径及公差、外沿法兰盘/面板尺寸与厚度。
   - 建立结构化【Product Specification Database】Markdown 表格。
3. 【02 渠道产品定位】：分析其在 {channel_mode} 货架上的生态位，拆解 Functional / Economic / Emotional 三重价值。
所有数据必须标注证据等级（【FACT】/【INFERENCE】等），严禁无据臆造。
"""
    p2 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 2: 场景矩阵、适配性与真实 VOC 挖掘】（涵盖 Node 03, 04, 05, 05.5）：
1. 【03 真实四维场景矩阵】：结合所选【安装部位: {mounting_type}】与【介质: {', '.join(selected_substrates)}】，交叉分析工况空间 × 载体材质 × 物理应力 × 潮湿及化学耐受环境。
2. 【04 适配性与安装干涉矩阵】：针对不同管道材质（PVC、ABS、旧铸铁管）及地面高度的物理适配状态（✓ Compatible / △ Conditional / ✕ Not Compatible）。禁止使用 "Fits All"！
3. 【05 真实买家 VOC 深度挖掘】：必须基于真实买家高频 1~5 星痛点。归纳出 Positive VOC、Negative VOC（密封不良漏水、法兰断裂、橡胶滑脱、螺栓位受力破损等）。
4. 【05.5 竞品 VOC 对标分析】：对比参考竞品（{competitors}），分析哪些差评是行业通病，哪些是该款特有缺陷。
"""
    p3 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 3: 根因归因、结构拆解与制造工艺】（涵盖 Node 06, 07, 07.5）：
1. 【06 差评根因归因链 (Root Cause)】：建立链条：买家抱怨 (Complaint) → 物理表象 (Symptom) → 根因 (Root Cause) → 归因分类（设计缺陷 / 制造缺陷 / 信息虚标 / 用户误用）。
2. 【07 物理结构拆解 (Teardown)】：拆解法兰主体、紧固机构、膨胀橡胶套环、不锈钢紧固螺栓等核心零配件，明确应力集中与断裂风险点。
3. 【07.5 制造工艺与质量风险】：分析塑料注塑工艺（ABS/PVC 缩水与熔接痕）、橡胶硫化公差及装配失效风险。
"""
    p4 = f"""{context_header}
基于前期结论，请严格执行《SOP V3.0》的【Stage 4: 商业数据库、机会排序与下一代产品定义】（涵盖 Node 08, 09, 09.5, 10, 11, 11.5, 12, 13, 14）：
1. 【08-09 竞品与规格数据库】：建立包含 EXACT, DIRECT, GENERIC, BENCHMARK 的多竞品横向比对表（含最新价格、评分、核心卖点）。
2. 【09.5 成本结构测算】：估算 BOM 材料、模具分摊、装配包装、海运落地成本，评估目标毛利率。
3. 【10 相似度量化评分】：制定权重矩阵，对关键竞品进行 0-100 分相似度打分并说明依据。
4. 【11-12 痛点排序与设计机会】：将痛点按频次与致命度排序，建立 `VOC → 根因 → 机会 → 结构改良` 的闭环。
5. 【13-14 下一代产品定义与 P0/P1/P2】：明确下一代改进型产品的物理参数、非妥协 Must-Have (P0)、体验升级 Should-Have (P1) 与差异化 (P2)。
"""
    p5 = f"""{context_header}
基于全部前期调研成果，请严格执行《SOP V3.0》的【Stage 5: 验证计划、渠道专属 Listing 与 20 问终极闭环】（涵盖 Node 15, 16, 17, 18）：
1. 【15 EVT / DVT / PVT 工程测试计划】：建立完整的工程验证矩阵（密封保压测试方法、扭矩破坏测试、耐化学老化、验收标准、绝不可随意写虚假 PASS）。
2. 【16 {channel_mode} 专属 Listing 策略】：
   - 符合该零售平台搜索推荐算法的 Product Title
   - Compatibility-First 核心 5 点特征 Bullet Points
   - 避免买错退货的旧管材质与尺寸兼容指南 (Compatibility Guide)
3. 【17 终版产品定义书 (Final Definition)】：系统提炼最终工程规格卡片。
4. 【18 终极闭环：解答 20 个产品开发核心决策问题】：逐一精确作答 20 个决策问题，为产品经理、结构工程师与海外买手提供立即可用的定论。
"""
    return [p1, p2, p3, p4, p5]

# ==============================================================================
# 7. 执行控制栏与流水线调用
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
            "Stage 1 物理架构与规格库",
            "Stage 2 场景适配与 VOC 挖掘",
            "Stage 3 根因归因与结构制造",
            "Stage 4 机会矩阵与下一代定义",
            "Stage 5 验证计划与 20 问闭环"
        ]
        search_queries = [
            f"{product_name} Home Depot price specifications dimensions review",
            f"{product_name} reviews complaints problems leakage fail",
            f"{product_name} teardown broken cracked rubber failure",
            f"{competitors} price rating comparison",
            f"{product_name} installation manual test standard"
        ]
        
        for idx in range(5):
            st.session_state[f"stage{idx+1}_res"] = execute_stage(
                provider, api_key, model_name, prompts[idx], stage_names[idx], 
                search_query=search_queries[idx], base_url_val=custom_base_url
            )
            if idx < 4:
                time.sleep(1)
        st.success("🎉 《北美建材大零售产品开发 SOP V3.0》全流程深度研究已执行完毕！")

# ==============================================================================
# 8. 多标签页呈现、单步独立重试与报告导出
# ==============================================================================
if any(st.session_state[f"stage{i}_res"] for i in range(1, 6)):
    tab1, tab2, tab3, tab4, tab5, tab_full = st.tabs([
        "📐 Stage 1: 规格基准库",
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

    render_stage_tab(tab1, 1, "Stage 1 规格基准库", f"{product_name} Home Depot price specifications")
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
