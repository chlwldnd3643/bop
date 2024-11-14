import sys
sys.path.append('C:/Users/Administrator/AppData/Local/Programs/FreeCAD 0.21/bin')
sys.path.append('C:/Users/Administrator/AppData/Local/Programs/FreeCAD 0.21/lib')
import FreeCAD

import freecad_utils
import random
import writejson

import numpy as np
import json

def genetic_algorithm(obj1, obj2, population_size, generations, mutation_rate, doc):
    def get_global_positions(bbox1, bbox2):
        return [
            min(bbox1.XMin, bbox2.XMin),  # X_MIN
            max(bbox1.XMax, bbox2.XMax),  # X_MAX
            min(bbox1.YMin, bbox2.YMin),  # Y_MIN
            max(bbox1.YMax, bbox2.YMax),  # Y_MAX
            min(bbox1.ZMin, bbox2.ZMin),  # Z_MIN
            max(bbox1.ZMax, bbox2.ZMax),  # Z_MAX
        ]
    bbox1 = obj1.Shape.BoundBox
    bbox2 = obj2.Shape.BoundBox
    X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX = range(6)
    global_positions = get_global_positions(bbox1, bbox2)# obj들은 초기에 충돌할 시 global bbox가 작으니 초기에 충돌시 둘 사이를 떨어뜨리는 작업이 필요합니다
    global_xmin = global_positions[X_MIN]
    global_xmax = global_positions[X_MAX]
    global_ymin = global_positions[Y_MIN]
    global_ymax = global_positions[Y_MAX]
    global_zmin = global_positions[Z_MIN]
    global_zmax = global_positions[Z_MAX]

    def check_and_apply_transformation(obj1, obj2, translation1, rotation1, translation2, rotation2):
        # 원래의 Placement를 백업합니다.
        original_placement1 = obj1.Placement.copy()
        original_placement2 = obj2.Placement.copy()

        try:
            # 새로운 변환을 객체에 적용합니다.
            obj1.Placement.Base = FreeCAD.Vector(*translation1)
            rotation_x1 = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), rotation1[0])
            rotation_y1 = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), rotation1[1])
            rotation_z1 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), rotation1[2])
            obj1.Placement.Rotation = rotation_x1.multiply(rotation_y1).multiply(rotation_z1)

            obj2.Placement.Base = FreeCAD.Vector(*translation2)
            rotation_x2 = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), rotation2[0])
            rotation_y2 = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), rotation2[1])
            rotation_z2 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), rotation2[2])
            obj2.Placement.Rotation = rotation_x2.multiply(rotation_y2).multiply(rotation_z2)

            doc.recompute()

            shape1 = obj1.Shape
            shape2 = obj2.Shape
            intersection = shape1.common(shape2).Volume

            doc.recompute()

            bbox1 = obj1.Shape.BoundBox
            bbox2 = obj2.Shape.BoundBox
            X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX = range(6)
            global_positions = get_global_positions(bbox1,
                                                    bbox2)  # obj들은 초기에 충돌할 시 global bbox가 작으니 초기에 충돌시 둘 사이를 떨어뜨리는 작업이 필요합니다
            global_xmin = global_positions[X_MIN]
            global_xmax = global_positions[X_MAX]
            global_ymin = global_positions[Y_MIN]
            global_ymax = global_positions[Y_MAX]
            global_zmin = global_positions[Z_MIN]
            global_zmax = global_positions[Z_MAX]

            return {
                'intersection_volume': intersection,
                'is_intersection': not bool(intersection > 0), #충돌시 False, 비충돌시 True
                'bbox_volume': (global_xmax - global_xmin) * (global_ymax - global_ymin) * (global_zmax - global_zmin)
            }

        finally:
            # 원래의 위치와 회전으로 복구합니다.
            obj1.Placement = original_placement1
            obj2.Placement = original_placement2

    def initialize_population(global_positions):
        population = []

        for _ in range(population_size):
            while True:
                individual = {
                    "position1": [random.uniform(-global_positions[2 * i]*2, global_positions[2 * i + 1]*2) for i in
                                  range(3)],
                    "rotation1": [random.randint(-2, 1) * 90 for _ in range(3)],
                    "position2": [random.uniform(-global_positions[2 * i]*2, global_positions[2 * i + 1]*2) for i in
                                  range(3)],
                    "rotation2": [random.randint(-2, 1) * 90 for _ in range(3)]
                }

                # 충돌 검사를 수행하여 유효한 개체인지 확인합니다.
                if check_and_apply_transformation(obj1, obj2, individual["position1"], individual["rotation1"],
                                                  individual["position2"], individual["rotation2"])['is_intersection']:
                    population.append(individual)
                    print("not collision during initilization")
                    break
                print("check and apply transformation and collision occured")
        print("Initializing : ", individual)
        return population


        # Evaluate fitness of each individual in the population
    def evaluate_fitness(individual):
        if check_and_apply_transformation(obj1, obj2, individual["position1"], individual["rotation1"],
                                                  individual["position2"], individual["rotation2"])["is_intersection"]:
            print("bbox volume", check_and_apply_transformation(obj1, obj2, individual["position1"], individual["rotation1"],
                                                  individual["position2"], individual["rotation2"])['bbox_volume'])
            return check_and_apply_transformation(obj1, obj2, individual["position1"], individual["rotation1"],
                                                  individual["position2"], individual["rotation2"])['bbox_volume']
        return 10e11  # Penalize colliding individuals

    # Selection function (roulette wheel selection)
    def select_parents(population, fitness_values):
        total_fitness = sum(fitness_values)
        if total_fitness == 0 or any(np.isnan(fitness_values)):
            probabilities = [1 / len(fitness_values)] * len(fitness_values)
        else:
            probabilities = [1 - f / total_fitness for f in fitness_values]
        probabilities = [0 if np.isnan(p) else p for p in probabilities]
        probabilities_sum = sum(probabilities)
        if probabilities_sum == 0:
            probabilities = [1 / len(probabilities)] * len(probabilities)
        else:
            probabilities = [p  / probabilities_sum for p in probabilities]
        selected_indices = np.random.choice(range(population_size), size=2, p=probabilities)
        return [population[selected_indices[0]], population[selected_indices[1]]]

    # Crossover function to combine two parents
    def crossover(parent1, parent2):
        # 비율 목록 중 하나를 무작위로 선택
        ratios = [(0, 1), (1, 2), (1, 1), (2, 1), (1, 0)]
        selected_ratio = random.choice(ratios)

        w1, w2 = selected_ratio

        def weighted_average(val1, val2, w1, w2):
            return (w1 * val1 + w2 * val2) / (w1 + w2)

        child = {
            "position1": [
                weighted_average(parent1["position1"][i], parent2["position1"][i], w1, w2)
                for i in range(len(parent1["position1"]))
            ],
            "rotation1": [
                weighted_average(parent1["rotation1"][i], parent2["rotation1"][i], w1, w2)
                for i in range(len(parent1["rotation1"]))
            ],
            "position2": [
                weighted_average(parent1["position2"][i], parent2["position2"][i], w1, w2)
                for i in range(len(parent1["position2"]))
            ],
            "rotation2": [
                weighted_average(parent1["rotation2"][i], parent2["rotation2"][i], w1, w2)
                for i in range(len(parent1["rotation2"]))
            ]
        }

        return child

    # Ensure that mutation occurs for both translation and rotation
    def mutate(individual, mutation_rate):
        while True:
            if random.random() < mutation_rate:
                individual["position1"] = [p * (1+random.uniform(-0.5, 0.5)) for p in best_individual["position1"]]
            if random.random() < mutation_rate:
                individual["rotation1"] = [r + random.randint(-2, 1)*90 for r in best_individual["rotation1"]]
            if random.random() < mutation_rate:
                individual["position2"] = [p * (1+random.uniform(-0.5, 0.5)) for p in best_individual["position2"]]
            if random.random() < mutation_rate:
                individual["rotation2"] = [r + random.randint(-2, 1)*90 for r in best_individual["rotation2"]]

            if check_and_apply_transformation(obj1, obj2, individual["position1"], individual["rotation1"],
                                           individual["position2"], individual["rotation2"])['is_intersection']:
                return individual

    # Main loop of genetic algorithm
    population=initialize_population(global_positions)
    best_individual = None
    best_fitness = 10e13 + 9000
    current_best_fitness = best_fitness
    current_best_individual = None

    for generation in range(generations):
        # Evaluate fitness of current population
        fitness_values = [evaluate_fitness(individual) for individual in population]

        # Handle NaN fitness values
        fitness_values = [10e13 if np.isnan(f) else f for f in fitness_values]

        # Find the best individual in the current generation
        current_best_fitness = min(fitness_values)
        current_best_individual = population[fitness_values.index(current_best_fitness)]


        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            best_individual = current_best_individual

            # Save the best individual's data to a JSON file
            best_data = {
                "transfer_position1_body": best_individual["position1"],
                "transfer_rotation1_body": best_individual["rotation1"],
                "transfer_position2_body": best_individual["position2"],
                "transfer_rotation2_body": best_individual["rotation2"]
            }
            with open("best_data.json", "w") as file:
                json.dump(best_data, file)

        print(
            f"Generation {generation + 1}: Best Fitness = {best_fitness}, current best fitness = {current_best_fitness}")
        if current_best_individual is not None:
            print("Part1 Pos:", current_best_individual["position1"], "Rev", current_best_individual["rotation1"])
            print("Part2 Pos:", current_best_individual["position2"], "Rev", current_best_individual["rotation2"])
        else:
            print("No valid individual found in this generation.")
        # Selection and reproduction
        new_population = []

        while len(new_population) < population_size:
            parent1, parent2 = select_parents(population, fitness_values)
            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate)
            new_population.append(child)

        # Replace old population with new population
        population = new_population[:population_size]

    # Print final result
    print("Basic Optimized Values:")
    print(best_individual)
    #best_data = {
    #    "transfer_position1_body": current_best_individual["position1"],
    #    "transfer_rotation1_body": current_best_individual["rotation1"],
    #    "transfer_position2_body": current_best_individual["position2"],
    #    "transfer_rotation2_body": current_best_individual["rotation2"]
    #}
    #with open("best_data.json", "w") as file:
    #    json.dump(best_data, file)
    print(f"Optimized Combined Bounding Box Volume: {best_fitness}")

