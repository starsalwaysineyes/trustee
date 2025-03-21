# Trustee系统时序图 - 模块化文件结构

本文件夹包含了按模块拆分的Trustee系统业务流程时序图文件。我们采用模块化的方式组织这些文件，以便于维护和理解。

## 文件结构

1. `common.puml` - 包含共享的样式定义和参与者声明
2. `initialization_phase.puml` - 初始化阶段的时序图
3. `task_execution_phase.puml` - 任务执行阶段的时序图
4. `exception_handling_phase.puml` - 异常处理阶段的时序图
5. `learning_optimization_phase.puml` - 学习与优化阶段的时序图
6. `complete_sequence.puml` - 整合所有阶段的完整时序图

## 参与者样式说明

时序图中使用了不同的形状来表示不同类型的组件：

- `actor` - 表示用户（外部角色）
- `boundary` - 表示用户交互层（系统边界）
- `control` - 表示视觉感知层和操作执行层（控制流程）
- `entity` - 表示任务理解层（核心业务逻辑）
- `database` - 表示安全控制层（数据存储）
- `collections` - 表示Windows系统（系统集合）

## 如何生成时序图

### 方法一：生成单个模块的时序图

如果您只想查看特定模块的时序图，可以使用以下命令：

```bash
java -jar plantuml.jar sequence_diagrams/initialization_phase.puml
```

这将生成`initialization_phase.png`文件。您可以替换文件名来生成其他模块的时序图。

### 方法二：生成完整时序图

如果您想查看包含所有阶段的完整时序图，请使用以下命令：

```bash
java -jar plantuml.jar sequence_diagrams/complete_sequence.puml
```

这将生成`complete_sequence.png`文件。

### 使用在线PlantUML服务

您也可以使用在线PlantUML服务：

1. 访问 [PlantUML在线编辑器](http://www.plantuml.com/plantuml/uml/)
2. 复制任意`.puml`文件的内容（注意在使用分模块文件时，需要将`!include common.puml`替换为common.puml的实际内容）
3. 点击"提交"按钮生成图表

## 注意事项

1. 使用分模块文件时，确保`common.puml`与其他文件位于同一目录
2. 如果您修改了参与者设置，只需更新`common.puml`文件，其他模块会自动继承这些更改
3. 如果您使用在线服务生成图表，需要将`!include`语句替换为实际内容
4. 所有文件都使用UTF-8编码，确保在编辑时保持此编码设置

## 扩展和定制

如果您需要为系统添加新的阶段或模块，只需创建新的`.puml`文件，并包含`common.puml`即可保持样式一致性。例如：

```plantuml
@startuml New_Phase
!pragma encoding utf-8
' 新阶段描述

' 包含共享样式和参与者定义
!include common.puml

title "Trustee系统 - 新阶段"

== "新阶段" ==
' 在此添加新阶段的时序逻辑

@enduml
```

## 与原始文件的关系

这些拆分的文件内容与原始的`sequence_diagram.puml`完全一致，只是进行了模块化组织，以便于维护和理解。完整流程文件`complete_sequence.puml`包含了与原始文件相同的全部内容。 