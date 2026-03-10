# 系统架构说明（中文）

## 1. 系统概览
本项目是一个基于命令行（CLI）的托福选词填空生成器。运行主链路如下：
1. 获取输入并合并配置。
2. 文本切句与分词。
3. 按规则筛选候选词，并按阶段执行放宽策略。
4. 调用选词策略（当前为同阶段候选等概率随机）。
5. 渲染挖空文本并输出答案文件。

## 2. 模块职责
1. `main.py` - 应用启动器。
- 仅负责启动 CLI 主入口。

2. `completetofelwords/cli.py` - 命令编排层。
- 解析命令行参数。
- 合并运行配置（优先级：CLI > `config.txt` > 默认值）。
- 支持交互式输入与参数校验。
- 组织端到端执行并处理用户可见错误。

3. `completetofelwords/pipeline.py` - 选词流水线协调器。
- 负责切句、分词、策略调用的流程编排。
- 对外提供稳定边界：`select_tokens(...)`。

4. `completetofelwords/selection_strategy.py` - 选词策略引擎。
- 定义策略接口：`SelectionStrategy`。
- 提供默认策略：`DefaultSelectionStrategy`。
- 执行候选词约束与分阶段放宽规则。
- 当前策略：同阶段候选词等概率无放回抽样。

5. `completetofelwords/sentence_splitter.py` - 句边界检测模块。
- 按 `. ! ?` 切句，并保留句子在原文中的字符跨度。

6. `completetofelwords/tokenizer.py` - 分词与位置映射模块。
- 抽取英文词 token。
- 为每个 token 记录句索引和字符位置。

7. `completetofelwords/lemmatizer.py` - 词元归一服务。
- 用于“词元唯一”规则的归一处理。
- 当前实现依赖 `PorterStemmer`（含降级行为）。

8. `completetofelwords/blank_renderer.py` - 挖空渲染引擎。
- 将命中词替换为占位符。
- 采用逆序替换确保字符位置不被前置替换破坏。

9. `completetofelwords/io_utils.py` - 输入输出与配置工具。
- 读取输入文本和词表。
- 解析 `config.txt`（`key=value`）。
- 解析输出路径并写入结果文件。

10. `completetofelwords/frequency_ranker.py` - 词频工具模块。
- 提供词频查询与权重计算工具函数。
- 当前默认策略使用该模块实现“先固定选 3 个高频词”。

## 3. 数据契约
1. `Token`（定义于 `tokenizer.py`）
- 原始词项，包含小写形式、句索引、字符起止位置。

2. `SelectedToken`（定义于 `selection_strategy.py`）
- 策略命中词项，包含词元信息与位置信息。

3. `PipelineResult`（定义于 `pipeline.py`）
- 输出命中词列表与警告信息列表。

## 4. 可扩展点
1. 自定义选词策略
- 实现 `SelectionStrategy.select(...)`。
- 通过 `select_tokens(..., strategy=...)` 注入。

2. NLP 模块升级
- 在不破坏数据契约的前提下替换切句、分词、词元归一实现。

3. 难度策略扩展
- 增加新策略类（例如分层策略、主题词优先策略），无需修改流水线协调器。

## 5. 运行时输出规则
1. `input/blanks/answers` 文件名均带 `YYYYMMDD` 日期后缀。
2. 输出前缀若以下划线开头，会自动去除前导下划线。
3. `input` 与 `blanks` 内容按 80 列自动换行。
4. 挖空前缀保留比例区间为 `[0.2, 0.6]`。

## 6. 测试覆盖面
1. `tests/test_pipeline.py` - 流水线规则与放宽行为。
2. `tests/test_selection_strategy.py` - 策略注入与高频优先行为。
3. `tests/test_config_fallback.py` - 配置回退与参数覆盖优先级。
4. `tests/test_cli_paths.py` - 输出文件命名与换行规则。
5. `tests/test_blank_renderer.py` - 挖空前缀比例区间。
