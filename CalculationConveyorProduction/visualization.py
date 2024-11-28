import matplotlib.pyplot as plt

def adjust_time_with_workers(t_base, c):
    """
    Корректирует время обработки с учетом количества рабочих.
    """
    if c == 0:
        return float('inf')
    return t_base / c

def calculate_times(goods, conveyors):
    """Рассчитывает T_посл, T_пар, T_опт с подробным выводом."""
    conveyors.sort(key=lambda x: x['m'])
    times = [conveyor['t'] / conveyor['c'] for conveyor in conveyors]
    times_str = " + ".join([f"{conveyor['t']:.2f}/{conveyor['c']:.2f}" for conveyor in conveyors])

    t_posl = sum(times) * goods
    t_posl_str = f"({times_str}) * {goods} = {sum(times):.2f} * {goods} = {t_posl:.2f}"

    t_par = sum([max(times) for _ in range(goods)]) + sum([min(times) for _ in range(goods)]) + sum([sorted(times)[1] for _ in range(goods)])
    times_par = [conveyor['t'] for conveyor in conveyors]
    t_par_str = f"({max(times_par)})*({goods}) + ({min(times_par)})*({goods}) + ({sorted(times_par)[1]})*({goods}) = {t_par}"

    t_opt = sum(times) + (goods - 1) * max(times)
    t_opt_str = f"({times_str}) + ({goods} - 1) * max({', '.join([str(t) for t in times])}) = {sum(times):.2f} + ({goods} - 1) * {max(times):.2f} = {sum(times) + (goods - 1) * max(times):.2f}"

    return t_posl, t_par, t_opt, t_posl_str, t_par_str, t_opt_str

def plot_conveyor_schedule(schedule, title,  t_posl_str=None, t_par_str=None, t_opt_str=None):
    """
    Строит график времени работы конвейеров.

    Args:
        schedule: Словарь, где ключ - номер конвейера (m), а значение - список интервалов времени работы [(start, length)].
        title: Заголовок графика.
    """
    plt.figure(figsize=(10, 6))
    
    yticks = []
    yticklabels = []
    
    for m, intervals in schedule.items():
        yticks.append(m)
        yticklabels.append(f"Конвейер {m}")
        plt.broken_barh(intervals, (m - 0.4, 0.8), facecolors='tab:blue')

    plt.yticks(yticks, yticklabels)
    plt.xlabel("Время")
    plt.ylabel("Конвейер")
    plt.title(title)
    plt.grid(True)

    if t_posl_str is not None:
        plt.text(0.05, 0.95, f"T_посл = {t_posl_str}", transform=plt.gca().transAxes, fontsize=11)
    if t_par_str is not None:
        plt.text(0.05, 0.90, f"T_пар = {t_par_str}", transform=plt.gca().transAxes, fontsize=11)
    if t_opt_str is not None:
        plt.text(0.05, 0.85, f"T_опт = {t_opt_str}", transform=plt.gca().transAxes, fontsize=11)

    
    plt.show()

def sequential_organization_schedule(goods, conveyors):
    """
    Создает расписание для последовательной организации.
    """
    conveyors.sort(key=lambda x: x['m'])
    for conveyor in conveyors:
        conveyor['t'] = adjust_time_with_workers(conveyor['t'], conveyor['c'])

    schedule = {}
    current_time = 0
    for conveyor in conveyors:
        m = conveyor['m']
        processing_time = conveyor['t'] * goods
        schedule[m] = [(current_time, processing_time)]
        current_time += processing_time

    return schedule

def parallel_organization_schedule(goods, conveyors):
    """
    Создает расписание для параллельной организации.

    Args:
        goods: Количество товаров.
        conveyors: Список конвейеров, каждый конвейер - словарь {'m': приоритет, 't': время обработки, 'c': количество рабочих}.

    Returns:
        Словарь с расписанием работы конвейеров.
    """
    conveyors.sort(key=lambda x: x['m'])
    for conveyor in conveyors:
        conveyor['t'] = adjust_time_with_workers(conveyor['t'], conveyor['c'])

    schedule = {conveyor['m']: [] for conveyor in conveyors}
    finish_times = [0] * goods

    for i in range(goods):
        current_time = 0
        for conveyor in conveyors:
            m = conveyor['m']
            if i == 0:
                start_time = current_time
                current_time += conveyor['t']
            else:
                start_time = max(current_time, finish_times[i - 1])
                current_time = start_time + conveyor['t']
            schedule[m].append((start_time, conveyor['t']))
        finish_times[i] = current_time

    return schedule

def optimized_continuous_schedule(goods, conveyors):
    """
    Создает оптимизированное расписание без простоя конвейеров.
    """
    conveyors.sort(key=lambda x: x['m'])
    for conveyor in conveyors:
        conveyor['t'] = adjust_time_with_workers(conveyor['t'], conveyor['c'])

    schedule = {conveyor['m']: [] for conveyor in conveyors}
    conveyor_finish_times = [0] * len(conveyors)
    goods_finish_times = [[0] * len(conveyors) for _ in range(goods)]

    for i in range(goods):
        for j, conveyor in enumerate(conveyors):
            m = conveyor['m']
            if j == 0:
                start_time = conveyors[j]['t'] * i  # Первый конвейер начинает работу сразу, как только появляется товар
            else:
                start_time = max(conveyor_finish_times[j], goods_finish_times[i][j - 1]) # если конвейер j свободен и предыдущий этап товара i закончен - начинаем

            finish_time = start_time + conveyor['t']
            schedule[m].append((start_time, conveyor['t']))
            conveyor_finish_times[j] = finish_time
            goods_finish_times[i][j] = finish_time

    return schedule


goods_count = 4
conveyors = [
    {'m': 1, 't': 2, 'c': 1},
    {'m': 2, 't': 3, 'c': 1},
    {'m': 3, 't': 1, 'c': 1}
]

t_posl, t_par, t_opt, t_posl_str, t_par_str, t_opt_str = calculate_times(goods_count, conveyors)
seq_schedule = sequential_organization_schedule(goods_count, conveyors.copy())
par_schedule = parallel_organization_schedule(goods_count, conveyors.copy())
optimized_schedule = optimized_continuous_schedule(goods_count, conveyors.copy())



plot_conveyor_schedule(seq_schedule, "Последовательная организация", t_posl_str=t_posl_str)
plot_conveyor_schedule(par_schedule, "Параллельная организация", t_par_str=t_par_str)
plot_conveyor_schedule(optimized_schedule, "Оптимизированная непрерывная организация", t_opt_str=t_opt_str)



print(f"$T_{{посл}} = {t_posl_str}")
print(f"$T_{{пар}} = {t_par_str}")
print(f"$T_{{опт}} = {t_opt_str}")