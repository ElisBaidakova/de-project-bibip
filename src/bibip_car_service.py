from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from pathlib import Path
import os
from collections import defaultdict


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

        Path(self.root_directory_path).mkdir(exist_ok=True)

        self.model_path = os.path.join(self.root_directory_path, 'models.txt')
        self.index_model = os.path.join(self.root_directory_path, 'model_index.txt')
        self.car_path = os.path.join(self.root_directory_path, 'cars.txt')
        self.index_car = os.path.join(self.root_directory_path, 'cars_index.txt')
        self.sale_path = os.path.join(self.root_directory_path, 'sales.txt')
        self.index_sale = os.path.join(self.root_directory_path, 'sales_index.txt')

        self.count_index_car = 0
        self.count_index_model = 0
        self.count_index_sale = 0

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        with open(self.model_path, mode='a', encoding='utf-8') as file_model, \
            open(self.index_model, mode='a', encoding='utf-8') as file_index_model:
            file_model.write(f'{model.id}, {model.name}, {model.brand.ljust(500)}\n')
            self.count_index_model += 1
            file_index_model.write(f'{model.name}, {self.count_index_model}\n')
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        with open(self.car_path, 'a', encoding='utf-8') as file_cars, \
            open(self.index_car, 'a', encoding='utf-8') as file_index_cars:
            file_cars.write(f'{car.vin}, {car.model}, {car.price}, {car.date_start}, {car.status.ljust(500)}\n')
            self.count_index_car += 1
            file_index_cars.write(f'{car.vin}, {self.count_index_car}\n')
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        with open(self.sale_path, mode='a', encoding='utf-8') as file_sale, \
            open(self.index_sale, mode='a', encoding='utf-8') as file_index_sale:
            # Записываем продажу в два файла
            file_sale.write(f'{sale.sales_number}, {sale.car_vin}, {sale.cost}, {sale.sales_date.ljust(500)}\n')
            self.count_index_sale += 1
            file_index_sale.write(f'{sale.sales_number}, {self.count_index_sale}\n')
        return car

    def find_car_by_vin(self, vin: str) -> Car | None:
        with open(self.index_car, 'r', encoding='utf-8') as file_index_cars:
            for line in file_index_cars:    # Ищем строку в индексе по vin коду
                parts = line.strip().split(', ')
                if len(parts) != 2:
                    continue
                indexed_vin, line_num_str = parts
                if indexed_vin == vin:
                    line_number = int(line_num_str) - 1  # Индексация в файле
                    break
                else:
                    return None  # VIN не найден
        # Читаем строку из файла cars.txt   
        with open(self.car_path, 'r', encoding='utf-8') as file_cars:
            lines = file_cars.readlines()
            if not (0 <= line_number < len(lines)):
                return None
            data = lines[line_number].strip().split(', ')
            if len(data) < 5:
                return None

            car_vin = data[0]
            model = data[1]
            price = float(data[2])
            date_start = data[3]
            raw_status = data[4].strip()    # Убираем лишние пробелы
            status = CarStatus(raw_status)
            # Создание и возврат объекта Car
            return Car(
                vin=car_vin,
                model=model,
                price=price,
                date_start=date_start,
                status=status
            )

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        with open(self.car_path, 'r', encoding='utf-8'):    # Читаем файл
            cars_available = list()    # Создаём список доступных авто
            if status == 'available':    # Если статус: доступен
                # Добавляем авто в список
                cars_available.append(self.car_path)
            cars_available.sort    # Сортируем список
        return cars_available

    # Задание 4. Детальная информация
    def get_car_info(self, line_number: int) -> CarFullInfo | None:
        with open(self.car_path, 'r', encoding='utf-8') as f_cars:
            car_lines = f_cars.readlines()    # Ищем авто по номеру строки
            if line_number < 0 or line_number >= len(car_lines):
                return None
            car_parts = car_lines[line_number].strip().split(', ')
            if len(car_parts) < 5:
                return None
            vin = car_parts[0]
            model_id = car_parts[1]
            price = float(car_parts[2])
            date_start = car_parts[3]
            status = CarStatus(car_parts[4].strip())

        # Ищем модель по model_id в models.txt
        model_name = None
        brand = None
        with open(self.model_path, 'r', encoding='utf-8') as f_models:
            for line in f_models:
                parts = line.strip().split(', ')
                if len(parts) < 3:
                    continue
                mid, name, padded_brand = parts[0], parts[1], parts[2]
                if mid == model_id:
                    model_name = name
                    brand = padded_brand.strip()  # убираем ljust(500)
                    break
    # Ищем продажу по VIN в sales.txt
        sales_date = None
        sales_cost = None
        sales_number = None
        with open(self.sale_path, 'r', encoding='utf-8') as f_sales:
            for line in f_sales:
                parts = line.strip().split(', ')
                if len(parts) < 4:
                    s_number, s_vin, cost, padded_date = parts
                if s_vin == vin:
                    sales_number = s_number
                    sales_cost = float(cost)
                    sales_date = padded_date.strip()

        return CarFullInfo(    # Создать и вернуть CarFullInfo
            vin=vin,
            model=Model(id=model_id, name=model_name, brand=brand),
            price=price,
            date_start=date_start,
            status=status,
            sales_number=sales_number,
            sales_date=sales_date,
            sales_cost=sales_cost
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car | None:
        target_line_number = None    # Ищем текущую строку автомобиля по VIN
        with open(self.index_car, 'r', encoding='utf-8') as f_index:
            for line in f_index:
                indexed_vin, line_num_str = line.strip().split(', ', 1)
                if indexed_vin == vin:
                    target_line_number = int(line_num_str) - 1
                    break
        if target_line_number is None:
            return None  # Старый VIN не найден
        # Обновляем VIN в cars.txt
        with open(self.car_path, 'r', encoding='utf-8') as f_cars:
            car_lines = f_cars.readlines()
        if not (0 <= target_line_number < len(car_lines)):
            return None
        parts = car_lines[target_line_number].strip().split(', ')
        if len(parts) < 5:
            return None

        parts[0] = new_vin    # Заменяем старый VIN на новый
        updated_line = ', '.join(parts) + '\n'
        car_lines[target_line_number] = updated_line
        # Перезаписываем файл автомобилей
        with open(self.car_path, 'w', encoding='utf-8') as f_cars:
            f_cars.writelines(car_lines)

        # Пересоздаём индексный файл cars_index.txt
        new_index_lines = []
        with open(self.car_path, 'r', encoding='utf-8') as f_cars:
            for idx, line in enumerate(f_cars, start=1):
                car_vin = line.strip().split(', ', 1)[0]
                new_index_lines.append(f"{car_vin}, {idx}\n")

        with open(self.index_car, 'w', encoding='utf-8') as f_index:
            f_index.writelines(new_index_lines)
        updated_car_data = updated_line.strip().split(', ')
        # Обновлённый объект Car
        return Car(
            vin=updated_car_data[0],
            model=updated_car_data[1],
            price=float(updated_car_data[2]),
            date_start=updated_car_data[3],
            status=CarStatus(updated_car_data[4].strip())
        )

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car | None:
        car_vin = None    # Ищем продажу по sales_number
        sale_line_index = None
        with open(self.sale_path, 'r', encoding='utf-8') as f_sales:
            sale_lines = f_sales.readlines()
        for i, line in enumerate(sale_lines):
            parts = line.strip().split(', ')
            if len(parts) >= 2 and parts[0] == sales_number:
                car_vin = parts[1]    # Получаем VIN автомобиля
                sale_line_index = i
        if car_vin is None:
            return None  # Продажа не найдена

        del sale_lines[sale_line_index]    # Удаляем запись о продаже
        with open(self.sale_path, 'w', encoding='utf-8') as f_sales:
            f_sales.writelines(sale_lines)
        # Ищем и обновляем статус автомобиля
        car_line_number = None   # Ищем номер строки авто по VIN через индекс
        with open(self.index_car, 'r', encoding='utf-8') as f_index:
            for line in f_index:
                indexed_vin, line_num_str = line.strip().split(', ', 1)
                if indexed_vin == car_vin:
                    car_line_number = int(line_num_str) - 1
        if car_line_number is None:
            return None  # Автомобиль не найден
        # Обновляем статус в cars.txt
        with open(self.car_path, 'r', encoding='utf-8') as f_cars:
            car_lines = f_cars.readlines()
        if not (0 <= car_line_number < len(car_lines)):
            return None
        parts = car_lines[car_line_number].strip().split(', ')
        if len(parts) < 5:
            return None
        parts[4] = CarStatus.AVAILABLE.value.ljust(500)    # Обновляем статус
        car_lines[car_line_number] = ', '.join(parts) + '\n'

        with open(self.car_path, 'w', encoding='utf-8') as f_cars:
            f_cars.writelines(car_lines)

        return Car(    # Обновлённый объект Car
            vin=parts[0],
            model=parts[1],
            price=float(parts[2]),
            date_start=parts[3],
            status=CarStatus.AVAILABLE
        )

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        sales_records = []    # Считываем все продажи
        with open(self.sale_path, 'r', encoding='utf-8') as f_sales:
            for line in f_sales:
                parts = line.strip().split(', ')
                if len(parts) >= 3:
                    vin = parts[1]
                    cost = float(parts[2])
                    sales_records.append((vin, cost))
        # Агрегируем данные по model_id
        model_data = defaultdict(lambda: {'count': 0, 'total_cost': 0.0})
        for vin, cost in sales_records:
            model_id = model_data.get(vin)
            if model_id is None:
                continue
            model_data[model_id]['count'] += 1
            model_data[model_id]['total_cost'] += cost

    # Сортируем по количеству продаж и по убыванию цены продажи
        def sort_key(item):
            model_id, stats = item
            count = stats['count']
            avg_cost = stats['total_cost'] / stats['count']
            return (-count, -avg_cost)  # минус для сортировки по убыванию
        sorted_models = sorted(model_data.items(), key=sort_key)

        result = []    # Возвращаем топ-3
        for model_id, stats in sorted_models[:3]:
            result.append(ModelSaleStats(
                model_id=model_id,
                count_sales=stats['count']
            ))
        return result
