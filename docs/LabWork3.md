# Лабораторная работа №3

## Задание
```
Тема: Использование принципов проектирования на уровне методов и классов
Цель работы: Получить опыт проектирования и реализации модулей с использованием принципов KISS, YAGNI, DRY, SOLID и др.

Ожидаемые результаты:
Для выбранного варианта использования:
Добавить ранее созданные или создать диаграммы контейнеров и компонентов нотации C4 model.
(1 балл)
Построить диаграмму последовательностей для выбранного варианта использования (показать взаимодействие C4-компонентов для реализации выбранного варианта использования).
(2 балла)
Построить модель БД в виде диаграммы классов UML. Если по заданию не предусмотрена БД, то самостоятельно продумать возможное хранилище данных, связанное с заданием. Минимально количество сущностей: 5.
(1 балл)
Реализовать требуемый клиентский и серверный код с учетом принципов KISS, YAGNI, DRY и SOLID. Пояснить, каким образом были учтены эти принципы.
(4  балла)

Повышенная сложность: Самостоятельно ознакомиться, кратко изложить и обосновать применимость или отказ по каждому принципу разработки в отдельности
(2 балла).
Рассмотреть следующие принципы разработки:
BDUF. Big design up front («Масштабное проектирование прежде всего»)
SoC. Separation оf concerns (принцип разделения ответственности)
MVP. Minimum viable pro duct (минимально жизнеспособный продукт)
PoC. Proof of concept (доказательство концепции)
```

## Отчет по лабораторной работе №3

##### Тема: Использование принципов проектирования на уровне методов и классов
##### Цель работы: Получить опыт проектирования и реализации модулей с использованием принципов KISS, YAGNI, DRY, SOLID и др.


### Диаграмма контейнеров

Диаграмма контейнеров детализирует компоненты системы, показывая ключевые контейнеры (модули) и их взаимодействие друг с другом. 
В данной архитектуре предполагается многозвенная (multi-tier) структура с выделенными контейнерами для пользовательского интерфейса, серверной логики и базы данных.

Пояснения по выбору архитектурного стиля:

1. Микросервисная архитектура - для взаимозаменяемости компонентов, бастрого проведения жкспериментов по улучшению взаимодействия с пользователем.
2. Сетевое взаимодействие: контейнеры общаются через REST API, что позволяет масштабировать и заменять отдельные модули.
3. Развертывание: каждый контейнер развертывается независимо, что упрощает обновления и поддержку системы.

##### Диаграмма:

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

### Диаграмма компонентов

Диаграмма компонентов иллюстрирует внутреннюю структуру контейнеров.

##### Компоненты API сервера:

1. Logger — компонент для записи логов запросов и ответов.
2. AuthService — компонент для проверки прав доступа и аутентификации.
3. NotificationService — отвечает за отправку уведомлений пользователям.
4. DataRepository — управляет операциями чтения и записи данных в базу данных.

##### Диаграмма:

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
left to right direction

package "LLM Service 1 - Docker" {
    [API 1] --> [Model 1]
    [API 1] --> [Monitoring 1]
}

package "LLM Service 2 - Docker" {
    [API 2] --> [Model 2]
    [API 2] --> [Monitoring 2]
}


package "Backend- K8s" {
    [Backend API] --> [Logger] : Накопление логов

    [Backend API] --> [Auth Service] : Авторизация и аунтефикация
    [Backend API] --> [Chat API] : Запрос к модели через чат
    [Chat API] --> [API 1]
    [Backend API] --> [Inline API] : Запрос к модели через редактор
    [Inline API] --> [API 2]

    [Backend API] --> [Health check] : Проверка состояния сервиса
    [Backend API] --> [Monitoring 1] : Проверка состояния сервиса
    [Backend API] --> [Monitoring 2] : Проверка состояния сервиса
}

package "IDE - local machine" {
    [IDE plugin] --> [Backend API] : Отправка запросов
}

@enduml
```

### Диаграмма последовательностей

Диаграмма последовательностей показывает взаимодействие компонентов системы в рамках одного сценария использования.

##### Диаграмма:
Взаимодействие с LLM сервисами 1 и 2 через API происходит одинаково, поэтому показано только взаимодействие с LLM сервисом 1.
```plantuml
@startuml

actor User
participant "IDE Plugin" as ide
participant "Backend API" as api
participant "LLM Service" as llm1
database "Logs Database" as db

title Inline request

User -> ide: Code editing
ide -> api: Request
api -> api: auth user

opt failed auth
    api -> ide: 400 Auth failed
end

api -> llm1: Request
llm1 -> api: 200 Response
opt failed response to llm1
    api -> ide: 500 Internal server error
end

api -> db: Log request
api -> ide: 200 Code suggestions

ide -> User: Code suggestions
User -> ide: Accept or reject suggestions
@enduml
```

### Модель БД

Данные, которые будут храниться в бд:
- авторизация пользователей

Данные, что будут храниться в логгере:
- логи запросов и ответов

```plantuml
@startuml
    
class User {
    + guid: str
    + login: str
    + password: str
}

class AccessToken {
    + guid: str
    + user_guid: str
    + token: str
    + start_timestamp: datetime
    + end_timestamp: datetime
}

User ||--o{ AccessToken : has
```

### Применение основных принципов разработки

В реализации FastAPI приложения были применены следующие принципы проектирования:

#### 1. KISS (Keep It Simple, Stupid)
Принцип реализован через:
- Простые и понятные эндпоинты с минимальным количеством параметров
- Прямолинейная обработка ошибок через HTTPException

#### 2. YAGNI (You Aren't Gonna Need It)
Принцип реализован через:
- Только необходимый минимум CRUD операций
- Отсутствие избыточной валидации или дополнительных полей
- Простая структура данных без усложнения на будущее

#### 3. DRY (Don't Repeat Yourself)
Принцип реализован через:
- Единообразная обработка ошибок
- Последовательное использование FastAPI для всех эндпоинтов
- Стандартизированный формат ответов

#### 4. SOLID
##### Single Responsibility Principle (SRP)
- Каждая функция отвечает только за одну операцию (создание, чтение, обновление или удаление)
- Четкое разделение между обработкой ошибок и бизнес-логикой

##### Open/Closed Principle (OCP)
- FastAPI позволяет легко расширять функциональность через наследование и middleware
- Структура позволяет добавлять новые эндпоинты без изменения существующих
- Возможно добавление новых контроллеров

##### Interface Segregation Principle (ISP)
- Каждый эндпоинт принимает только те параметры, которые ему необходимы
- Нет избыточных интерфейсов или параметров

##### Dependency Inversion Principle (DIP)
- Использование FastAPI обеспечивает слабую связанность компонентов
- Зависимости могут быть легко заменены (например, хранилище данных)

### Дополнительные принципы разработки

#### BDUF (Big Design Up Front)
- Архитектура достаточно проста, сервис может быть масштабирован в K8s

#### SoC (Separation of Concerns)
Принцип применен в проекте:
- Разделение кода на отдельные эндпоинты для разных операций (create, read, update, delete)
- Отделение бизнес-логики (работа с данными) от обработки HTTP-запросов
- Выделение обработки ошибок в отдельный механизм через HTTPException
- Четкое разграничение ответственности между функциями

#### MVP (Minimum Viable Product)
Принцип активно применяется в проекте:
- Реализован минимально необходимый набор CRUD операций
- Использовано простейшее хранилище данных (словарь)
- Минимальная, но достаточная валидация данных
- Отсутствие избыточного функционала

#### PoC (Proof of Concept)
Данная реализация служит proof of concept, демонстрируя:
- Возможность построения REST API с минимальными затратами
- Применимость принципов SOLID в простом веб-приложении
- Работоспособность базового CRUD-функционала
- Эффективность FastAPI для создания простых веб-сервисов
