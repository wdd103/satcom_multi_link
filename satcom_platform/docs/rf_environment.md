# 大气传播模型

网页「场景参数 → 大气传播效应」提供雨衰、气体吸收、云雾衰减、对流层闪烁四个独立开关。修改后点击顶部「保存」，再启动仿真。旧项目缺省关闭，保持原有计算基线。

| YAML 字段（propagation 下） | 关闭值 | 启用值 |
| --- | --- | --- |
| rain_model | NONE | ITU_R_P618 |
| atmosphere_model | NONE | ITU_R_P676 |
| cloud_fog_model | NONE | ITU_R_P840 |
| tropo_scintillation_model | NONE | ITU_R_P618 |

运行时查询本机 STK 可选模型，并选择对应推荐书的最新已安装版本。本机 STK 12.6 验证得到雨衰 P.618-13、气体吸收 P.676-9、云雾 P.840-7、对流层闪烁 P.618-12。不支持时运行报错，不静默忽略开关。除场景级雨衰开关外，程序也设置各接收机的 UseRain 与 RainOutagePercent，包括飞机接收机及卫星接收机。

| 可编辑参数 | 缺省值 | 校验范围 |
| --- | --- | --- |
| rain_outage_percent（雨衰超越概率，%） | 0.1 | 0.001–5 |
| scintillation_outage_percent（闪烁超越概率，%） | 0.1 | 0.01–50 |
| cloud_ceiling_m（云顶高度，m） | 3000 | 0–20000 |
| cloud_thickness_m（云层厚度，m） | 500 | 0–20000，且不超过云顶高度 |
| cloud_temperature_k（云温，K） | 273.15 | 200–330 |
| cloud_liquid_water_density_g_m3（云液态水密度，g/m³） | 0.5 | 0–10 |

这些是平台采用的输入范围。气体吸收和云雾模型仅接受 1–1000 GHz，雨衰 1–55 GHz，对流层闪烁 4–20 GHz。当前 12/14 GHz 配置在范围内。闪烁超越概率在写入 STK 时从百分数转换为比例，云液态水密度写入时显式携带单位。

运行结果新增 `rf_environment.json`，记录请求配置、本机选用模型和 STK 环境回读；同样写入 manifest 和场景压缩包。`link_budget.csv` 新增 `rain_loss_db`、`gas_loss_db`、`cloud_fog_loss_db`、`tropo_scintillation_loss_db`，全部直接读取 STK Link Information；不可见时为空。原有 C/N、Eb/No、BER 由同一 STK 预算输出，OMNeT++ 时间线继承其结果。

模型计算的是统计衰减，不生成真实天气或随机衰落时间序列。损耗是否发生取决于 STK 模型的高度与路径适用条件，例如高空飞机向卫星的路径可能不穿过雨云。四项分别启用，使用 STK 默认的独立损耗合成方式；未启用 P.618 第 2.5 节联合统计合成。接收机继续使用原来的固定 G/T、噪声温度配置，本次没有增加天气噪声温度自动计算。

验证：`python -m unittest discover -s tests -q`；`node tests/test_rf_controls.cjs`。在安装 STK 及 pywin32 的 Windows 环境设置 `PYTHONPATH=src` 后，可运行 `python scripts/probe_rf_environment.py`，以独立、不保存的临时场景验证四项模型分别开启、共同开启及关闭恢复基线的 C/N、Eb/No、BER 和损耗结果。

2026-11-25 本机验证：17 项 Python 测试通过，前端四个开关的启用、禁用及保存请求检查通过。STK 独立模型测试分别确认四项开启后损耗增加、C/N 下降，关闭后恢复基线。临时示例项目选择 SAT41923，四项全部启用，完成四条链路、244 行预算（178 行有效采样）、STK 场景保存和压缩包导出；网关上行样例的雨衰、气体吸收、云雾、闪烁损耗分别约 24.116、0.585、0.434、2.362 dB。这些数值仅验证集成链路，不代表实际飞行性能。更新后的本地服务及新版静态资源返回 HTTP 200；浏览器界面视觉检查因自动化窗口/本地连接限制未完成。

参考：[STK RF Environment](https://help.agi.com/stk/12.7.1/Content/comm/CommRadar02-01.htm)、[RFEnvironment Connect](https://help.agi.com/stk/Subsystems/connectCmds/Content/cmd_RFEnvironment.htm)。
