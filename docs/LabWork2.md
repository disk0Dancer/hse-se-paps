# Лабораторная работа №2
```
Тема: Использование нотации C4 model для проектирования архитектуры программной системы
Цель работы: Получить опыт использования графической нотации для фиксации архитектурных решений

## Ожидаемые результаты
1. Диаграмма системного контекста (3 балла)
2. Диаграмма контейнеров с пояснениями по выбору базового архитектурного стиля / архитектуры уровня приложений (при этом выбрать топологию, подразумевающую несколько модулей развертывания и наличие сетевого взаимодействия) (5 баллов)

Повышенная сложность:
- Диаграмма компонентов (2 балла)
```
---

# Использование нотации C4 model для проектирования архитектуры программной системы

## 1. Диаграмма системного контекста
*Диаграмма системного контекста* определяет систему интеграции LLM в IDE, взаимодействия с внешними пользователями и сервисами.
Основные участники — разработчики, использующие IDE с интегрированным помощником на базе LLM, и внешние системы аутентификации.

Система помогает разработчикам, предоставляя интеллектуальные подсказки и анализ кода с помощью LLM.

Пользователи входят в IDE, а аутентификация проходит через токен, полученный после регистрации. Также есть взаимодействие с внешним сервисом для обучения и обновления LLM.

*Диаграмма:*

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
left to right direction
skinparam actorStyle awesome

title System Context diagram

System(llmSystem, "LLM-based Code Assistant in IDE") {
}
System_Ext(idePlugin, "IDE Plugin", "React+Kotlin", "Interface for LLM interaction")
System_Ext(gitlab, "GitLab", "VCS + Auth")

Person(SH1, "Technical Director")
Person(SH2, "Director of CyberSec")
Person(SH3, "Project Manager")
Person(SH4, "Technical Manager")
Person(SH5, "Developer")
Person(SH6, "Product Development Team")
Person(SH7, "Technical Support")
Person(SH8, "Financial Director")

SH6 --> gitlab : "Monitors CI/CD pipelines"
SH1 --> llmSystem : "Requests performance reports"
SH2 --> llmSystem : "Ensures data security and logs interactions"
SH3 --> llmSystem : "Monitors project progress"
SH4 --> llmSystem : "Configures and integrates the system"
SH5 --> idePlugin : "Uses the system for code suggestions"

SH7 --> llmSystem : "Monitors system health and accesses documentation"
SH8 --> llmSystem : "Requests cost reports"

idePlugin --> llmSystem : "Sends LLM responses"
llmSystem <-- gitlab : "Sends deployment data"
llmSystem --> gitlab : "Authenticates users"
@enduml
```

## 2. Диаграмма контейнеров

Диаграмма контейнеров детализирует компоненты системы, показывая ключевые контейнеры (модули) и их взаимодействие друг с другом.
Вданной архитектуре предполагается многозвенная (multi-tier) структура с выделенными контейнерами для пользовательского интерфейса, серверной логики и базы данных.

Пояснения по выбору архитектурного стиля:
- Микросервисная архитектура - для взаимозаменяемости компонентов, бастрого проведения жкспериментов по улучшению взаимодействия с пользователем.
- Сетевое взаимодействие: контейнеры общаются через REST API, что позволяет масштабировать и заменять отдельные модули.
- Развертывание: каждый контейнер развертывается независимо, что упрощает обновления и поддержку системы.

**Диаграмма:**
импорт компонент
```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Container diagram

Person(cto, "Technical Director")
Person(cyber, "Director of CyberSec")
Person(pm, "Project Manager")
Person(tech, "Technical Manager")
Person(dev, "Developer")
Person(devteam, "Product Development Team")
Person(support, "Technical Support")
Person(fin, "Financial Director")

System_Ext(idePlugin, "IDE Plugin", "React+Kotlin", "Interface for LLM interaction")
System_Ext(gitlab, "GitLab", "VCS + Auth")

Container_Boundary(llmSystem, "LLM-based Code Assistant in IDE") {
    Container_Boundary(back, "api") {
        Container(backend, "Backend API", "Python(FastAPI)", "Handles requests from IDE plugin")
        ContainerDb(database, "Logs Database", "PostgreSQL", "Stores requests and responses")
    }
    Container(llmService1, "LLM Service1", "Python(Vllm)", "Processes requests and generates responses")
    Container(llmService2, "LLM Service2", "Python(Vllm)", "Processes requests and generates responses")
}

devteam --> gitlab : "Monitors CI/CD pipelines"
cto --> llmSystem : "Requests performance reports"
cyber --> llmSystem : "Ensures data security and logs interactions"
pm --> llmSystem : "Monitors project progress"
tech --> llmSystem : "Configures and integrates the system"
dev --> idePlugin : "Uses the system for code suggestions"

devteam --> llmSystem : "Monitors system health and accesses documentation"
fin --> llmSystem : "Requests cost reports"

idePlugin --> backend : "Sends LLM responses"
backend --> gitlab : "Authenticates users"
backend <--> llmService1 : "Code generation request"
backend <--> llmService2 : "Code generation request"
backend --> database: "Log usage data"

support --> llmSystem: "llmSystem"
backend --> llmService1 : "healtcheck"
backend --> llmService2 : "healtcheck"
backend --> database: "healtcheck"


llmSystem <-- gitlab : "Sends deployment data"
@enduml
```

## 3. Диаграмма компонентов

Диаграмма компонентов иллюстрирует внутреннюю структуру контейнеров.

Компоненты API сервера:
- Logger — компонент для записи логов запросов и ответов.
- AuthService — компонент для проверки прав доступа и аутентификации.
- NotificationService — отвечает за отправку уведомлений пользователям.
- DataRepository — управляет операциями чтения и записи данных в базу данных.

Диаграмма:
```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
left to right direction
Person(dev, "Developer")
System_Ext(idePlugin, "IDE Plugin", "React+Kotlin", "Interface for LLM interaction")
System_Ext(gitlab, "GitLab", "VCS + Auth")

Container(llmService1, "LLM Service1", "Python(Vllm)", "Processes requests and generates responses")
Container(llmService2, "LLM Service2", "Python(Vllm)", "Processes requests and generates responses")


Container_Boundary(back, "api") {
    Container(gateway, "Gateway API")
    Container(chat, "Chat API")
    Container(inline, "Inline API")
    Container(healthcheck, "healthcheck")
    Container(logger, "logger")
    Container(auth, "auth")
}
ContainerDb(database, "Logs Database", "PostgreSQL", "Stores requests and responses")



dev --> idePlugin
idePlugin --> gateway
[gateway] --> [logger] : Накопление логов
logger --> database
gateway --> auth 
auth --> gitlab : Авторизация и аунтефикация

[gateway] --> [chat] : Запрос к модели через чат
[chat] --> [llmService1]
[gateway] --> [inline] : Запрос к модели через редактор
[inline] --> [llmService2]

[gateway] --> [healthcheck] : Проверка состояния сервиса
[healthcheck] --> [llmService1] : Проверка состояния сервиса
[healthcheck] --> [llmService2] : Проверка состояния сервиса


@enduml
```
