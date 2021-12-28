import numpy as np


class ImperialData:
    def __init__(self, xcount, ycount) -> None:
        self.data = np.empty(
            (xcount, ycount),
        )
        self.ycount = ycount
        self.xcount = xcount

    def store_data(self, i1, i2, txt):
        if txt.strip() == "":
            self.data[i1][i2] = np.nan
        else:
            txt = txt.replace(" ", "").replace(",", "").replace(".", "")
            self.data[i1][i2] = int(txt)

    def get_data_txt(self, i1, i2):
        data = self.data[i1, i2]
        if np.isnan(data):
            return ""
        else:
            return str(int(data))

    def check_row(self, row):
        errors = []
        return errors
        row_data = np.nan_to_num(self.data[row], copy=True)
        for offset in [2, 5, 8]:
            if row_data[offset + 0] != row_data[offset + 1] + row_data[offset + 2]:
                errors.extend([offset + 0, offset + 1, offset + 2])
        return errors

    def export(self, name):
        np.savetxt("{}.dat".format(name), self.data)
