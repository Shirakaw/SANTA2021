def CSVLine2Matrix(csv_file_name: str):
    matrix_list = []
    with open(csv_file_name, encoding="UTF-8") as fp:
        line = fp.readline()
        while line:
            line = fp.readline()
            if line:
                # ['\uf8ffüéÖ\uf8ffü§∂\uf8ffü¶å\uf8ffüéÄ', '7', '7', '7'] 保留序列1及之后的数组
                matrix_list.append(line.split(',')[1:])
    return matrix_list


distance_matrox = CSVLine2Matrix('distance_matrix.csv')
print(distance_matrox)
