from volumetric_viewer.transfer_function import TransferFunction


class TransferFunctionManager:

    def __init__(self):
        self._transfer_function = TransferFunction()
    
    def update_transfer_function(self, data: dict):
        self._transfer_function.update(data["color_knots"], data["alpha_knots"])

    def read_file(self, filename: str):
        data = {
            "alpha_knots": [],
            "color_knots": []
        }

        with open(file=filename) as file:
            for line in file:
                values = line.strip().split()
                if len(values) == 2:
                    data["alpha_knots"].append((float(values[0]), float(values[1])))
                elif len(values) == 4:
                    data["color_knots"].append((float(values[0]), float(values[1]), float(values[2]), float(values[3])))

        return data
    
    def write_file(self, filename: str):
        with open(filename, 'w') as file:
            for knot in self._transfer_function.get_alpha_knots():
                file.write(f"{knot[0]} {knot[1]}\n") 

            for knot in self._transfer_function.get_color_knots():
                file.write(f"{knot[0]} {knot[1]} {knot[2]} {knot[3]}\n") 

    def bind_transfer_function(self, texture_unit):
        self._transfer_function.bind(texture_unit)
