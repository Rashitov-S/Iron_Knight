# Iron Knight

## Описание проекта
**Iron Knight** — это игра в жанре экшн-платформера, разработанная на Python с использованием библиотеки Pygame. Игрок управляет рыцарем, который должен пройти через множество уровней, сражаясь с врагами, избегая ловушек и собирая монеты. Игра также позволяет игрокам создавать собственные уровни, что добавляет элемент творчества и реиграбельности.

## Цель игры
Цель игры — пройти все уровни, собирая как можно больше монет и улучшая характеристики персонажа. Игроку предстоит преодолевать опасные ловушки, сражаться с врагами и открывать сундуки с сокровищами.

## Управление
- **Движение влево/вправо:** Клавиши **A** и **D** или стрелки влево/вправо.
- **Прыжок:** Клавиша **SPACE**.
- **Атака:** Клавиша **Z** или левая кнопка мыши.

## Основные элементы игры

### Главное меню
В главном меню игрок может:
- Продолжить существующую игру.
- Начать новую игру.

Прогресс автоматически сохраняется при переходе на новый уровень.

### Игрок
У игрока есть несколько анимаций, включая:
- Бег.
- Прыжки.
- Атака 1.
- Атака 2.
- Смерть.
- Падение.

### Счетчики
На экране отображаются три основных показателя:
- **Здоровье:** Количество жизней игрока.
- **Выносливость:** Используется для выполнения действий, таких как атака.
- **Монеты:** Собираются на уровнях и используются для улучшений в магазине.

### Враги
В игре присутствуют различные типы врагов:
- **Скелеты:** Простые враги, которые ходят и атакуют игрока.
- **Мухоморы:** Более опасные враги с уникальными атаками.
- **Лучники:** Враги, которые атакуют на расстоянии.

С каждым уровнем урон от врагов увеличивается.

### Магазин
В магазине игрок может улучшить характеристики персонажа:
- **Сила:** Увеличивает урон от атак.
- **Здоровье:** Увеличивает максимальное количество здоровья.
- **Выносливость:** Увеличивает максимальную выносливость.

Каждое улучшение стоит **250 монет**.

### Ловушки
На уровнях присутствуют различные ловушки, которые наносят урон:
- **Огонь:** Наносит урон при контакте.
- **Электрическое поле:** Наносит урон при приближении.
- **Ядовитое облако:** Наносит урон со временем.

### Сундуки
Сундуки содержат случайное количество монет, которые игрок может собрать для улучшения своих характеристик.

### Проигрыш
Если игрок погибает, текущий уровень перезапускается, а показатели здоровья и выносливости возвращаются к исходным значениям.

### Финальное окно
После прохождения последнего уровня и входа в портал, игроку показывается победное окно с количеством собранных монет.

## Установка и запуск
1. Убедитесь, что у вас установлен Python 3.x.
2. Скачайте или клонируйте репозиторий с игрой.
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Запустите игру:
   ```bash
   python map.py
   ```
