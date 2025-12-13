from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from pathlib import Path
import os
from collections import defaultdict
from typing import Dict, Any


class CarService:

    # Ширина полей для выравнивания в текстовых файлах
    BRAND_WIDTH = 500
    STATUS_WIDTH = 500

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
        # Формируем строку: сначала данные, потом дополняем бренд пробелами
        brand_padded = model.brand.ljust(self.BRAND_WIDTH)
        line = f"{model.id}, {model.name}, {brand_padded}\n"

        with open(self.model_path, mode='a', encoding='utf-8') as file_model, \
             open(self.index_model, mode='a', encoding='utf-8') as file_index_model:
            file_model.write(line)
            self.count_index_model += 1
            file_index_model.write(f"{model.name}, {self.count_index_model}\n")
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        # Формируем строку: сначала данные, потом дополняем статус пробелами
        status_padded = car.status.value.ljust(self.STATUS_WIDTH)
        line = f"{car.vin}, {car.model}, {car.price}, {car.date_start}, {status_padded}\n"

        with open(self.car_path, mode='a', encoding='utf-8') as file_cars, \
             open(self.index_car, mode='a', encoding='utf-8') as file_index_cars:
            file_cars.write(line)
            self.count_index_car += 1
            file_index_cars.write(f"{car.vin}, {self.count_index_car}\n")
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car | None:
        car_line_number = None
        # Ищем автомобиль по VIN
        with open(self.index_car, 'r', encoding='utf-8') as f_index:
            for line in f_index:
                parts = line.strip().split(', ')
                if len(parts) == 2 and parts[0] == sale.car_vin:
                    car_line_number = int(parts[1]) - 1
        if car_line_number is None:
            return None  # Автомобиль не найден

        car_data = None
        with open(self.car_path, 'r', encoding='utf-8') as f_cars:
            lines = f_cars.readlines()    # Читаем данные автомобиля
            if not (0 <= car_line_number < len(lines)):
                return None
        parts = lines[car_line_number].strip().split(', ')
        if len(parts) < 5:
            return None

        vin = parts[0]
        model = parts[1]
        price = float(parts[2])
        date_start = parts[3]
        car_data = (vin, model, price, date_start)

        # Обновляем статус автомобиля
        vin, model, price, date_start = car_data
        new_status_str = CarStatus.sold.value.ljust(self.STATUS_WIDTH)
        updated_line = f"{vin}, {model}, {price}, {date_start}, {new_status_str}\n"

        with open(self.car_path, 'r', encoding='utf-8') as f_cars:
            all_lines = f_cars.readlines()
        all_lines[car_line_number] = updated_line
        with open(self.car_path, 'w', encoding='utf-8') as f_cars:
            f_cars.writelines(all_lines)

        if isinstance(sale.sales_date, str):
            sales_date_str = sale.sales_date
        else:
            sales_date_str = str(sale.sales_date)    # Приведение к строке

        sales_date_padded = sales_date_str.ljust(self.STATUS_WIDTH)
        sale_line = f"{sale.sales_number}, {sale.car_vin}, {sale.cost}, {sales_date_padded}\n"

        with open(self.sale_path, 'a', encoding='utf-8') as f_sale, \
             open(self.index_sale, 'a', encoding='utf-8') as f_index_sale:
            f_sale.write(sale_line)
            self.count_index_sale += 1
            f_index_sale.write(f"{sale.sales_number}, {self.count_index_sale}\n")
        # Возвращаем объект Car с обновлённым статусом
        return Car(
            vin=vin,
            model=model,
            price=price,
            date_start=date_start,
            status=CarStatus.sold
        )

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        cars = []
        with open(self.car_path, 'r', encoding='utf-8') as file_cars:
            for line in file_cars:
                line = line.strip()
                if not line:
                    continue    # пропускаем пустые строки
                parts = line.split(', ')
                if len(parts) < 5:
                    continue    # некорректная строка
                vin = parts[0]    # Извлекаем данные
                model = parts[1]
                price = float(parts[2])
                date_start = parts[3]
                raw_status = parts[4].strip()
            car_status = CarStatus(raw_status)    # Сравниваем статус
            if car_status == status:
                cars.append(Car(
                    vin=vin,
                    model=model,
                    price=price,
                    date_start=date_start,
                    status=car_status
                ))
        cars.sort(key=lambda car: car.vin)    # Сортируем по VIN
        return cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        with open(self.index_car, 'r', encoding='utf-8') as f_index:
            for line in f_index:    # Ищем автомобиль по VIN
                parts = line.strip().split(', ')
                if len(parts) == 2 and parts[0] == vin:
                    line_number = int(parts[1]) - 1
                else:
                    return None  # VIN не найден в индексе

        with open(self.car_path, 'r', encoding='utf-8') as f_cars:
            car_lines = f_cars.readlines()    # Читаем строку автомобиля
        if not (0 <= line_number < len(car_lines)):
            return None
        car_parts = car_lines[line_number].strip().split(', ')
        if len(car_parts) < 5:
            return None

        vin = car_parts[0]
        model_id = car_parts[1]
        price = float(car_parts[2])
        date_start = car_parts[3]
        status = CarStatus(car_parts[4].strip())

        model_name = None    # Ищем модель по model_id
        brand = None
        with open(self.model_path, 'r', encoding='utf-8') as f_models:
            for line in f_models:
                parts = line.strip().split(', ')
                if len(parts) >= 3:
                    mid, name, padded_brand = parts[0], parts[1], parts[2]
                    if mid == model_id:
                        model_name = name
                        brand = padded_brand.strip()

        sales_number = None    # Ищем продажу по VIN
        sales_cost = None
        sales_date = None
        with open(self.sale_path, 'r', encoding='utf-8') as f_sales:
            for line in f_sales:
                parts = line.strip().split(', ')
                if len(parts) >= 4:  # ← ИСПРАВЛЕНО: должно быть >= 4
                    s_number, s_vin, cost, padded_date = parts[0], parts[1], parts[2], parts[3]
                    if s_vin == vin:
                        sales_number = s_number
                        sales_cost = float(cost)
                        sales_date = padded_date.strip()
        # Создаём и возвращаем CarFullInfo
        return CarFullInfo(
            vin=vin,
            model=Model(id=model_id, name=model_name or "", brand=brand or ""),
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

        if car_vin is None or sale_line_index is None:
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
        parts[4] = CarStatus.available.value.ljust(500)    # Обновляем статус
        car_lines[car_line_number] = ', '.join(parts) + '\n'

        with open(self.car_path, 'w', encoding='utf-8') as f_cars:
            f_cars.writelines(car_lines)

        return Car(    # Обновлённый объект Car
            vin=parts[0],
            model=parts[1],
            price=float(parts[2]),
            date_start=parts[3],
            status=CarStatus.available
        )

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        sales_records: list[tuple[str, float]] = []
        # Считываем все продажи: (vin, cost)
        with open(self.sale_path, 'r', encoding='utf-8') as f_sales:
            for line in f_sales:
                parts = line.strip().split(', ')
                if len(parts) >= 3:
                    vin = parts[1]
                    cost = float(parts[2])
                    sales_records.append((vin, cost))
                if not sales_records:
                    return []

        vin_to_model: dict[str, str] = {}
        with open(self.car_path, 'r', encoding='utf-8') as f_cars:
            for line in f_cars:
                parts = line.strip().split(', ')
                if len(parts) >= 2:
                    vin = parts[0]
                    model_id = parts[1]
                    vin_to_model[vin] = model_id

        # Агрегируем данные по model_id
        model_data: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'count': 0, 'total_cost': 0.0})
        for vin, cost in sales_records:
            if vin in vin_to_model:
                model_id = vin_to_model[vin]  # тип: str
                model_data[model_id]['count'] += 1
                model_data[model_id]['total_cost'] += cost

        # Сортируем по количеству продаж и по средней цене
        def sort_key(item: tuple[str, dict[str, Any]]) -> tuple[int, float]:
            model_id, stats = item
            count = stats['count']
            avg_cost = stats['total_cost'] / stats['count']
            return (-count, -avg_cost)

        sorted_models = sorted(model_data.items(), key=sort_key)

        # Возвращаем топ-3
        result: list[ModelSaleStats] = []
        for model_id, stats in sorted_models[:3]:
            result.append(ModelSaleStats(
                model_id=model_id,
                count_sales=stats['count']
            ))
        return result
