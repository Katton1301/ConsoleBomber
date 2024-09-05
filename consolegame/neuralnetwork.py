import numpy as np
# from mpl_toolkits.axes_grid1 import make_axes_locatable
# import matplotlib.pyplot as plt
# from sklearn import preprocessing
import json
import torch
import os


class GameNet(torch.nn.Module):
    def __init__(self, file_name):
        super(GameNet, self).__init__()

        self.scaling_B_coord = []  # изначально пустой
        data = None
        self.modelName = None
        self.genData = None
        # noinspection PyBroadException
        try:
            with open(file_name, "r") as json_file:
                data = json.load(json_file)
        except Exception:
            pass
        if data:
            if 'net' in data:
                dimension_list = []
                json_net = data['net']
                if 'num_iter' in json_net:
                    self.num_iter = json_net['num_iter']
                if 'train_number' in json_net:
                    self.train_number = json_net['train_number']
                if 'layers' in json_net:
                    self.inputN = json_net['layers']['inputLayer']
                    dimension_list = [self.inputN]
                    if 'innerLayers' in json_net['layers']:
                        dimension_list += json_net['layers']['innerLayers']
                    if 'outputLayer' in json_net['layers']:
                        dimension_list += [json_net['layers']['outputLayer']]
                if 'val_number' in json_net:
                    self.val_number = json_net['val_number']
                if 'resave' in json_net:
                    self.resave = json_net['resave']
                if 'learning_rate' in json_net:
                    self.learning_rate = json_net['learning_rate']
                if 'weight_decay' in json_net:
                    self.weight_decay = json_net['weight_decay']
                if 'loadData' in json_net:
                    if 'genData' in json_net['loadData']:
                        self.genData = json_net['loadData']['genData']
                    if 'modelName' in json_net['loadData']:
                        self.modelName = json_net['loadData']['modelName']

                self.nnArc = torch.nn.Sequential(
                    torch.nn.Linear(dimension_list[0], dimension_list[1]),
                    torch.nn.ELU()
                )
                for i in range(1, len(dimension_list) - 1):
                    self.nnArc.append(torch.nn.BatchNorm1d(dimension_list[i]))
                    self.nnArc.append(torch.nn.Linear(dimension_list[i], dimension_list[i + 1]))
                    self.nnArc.append(torch.nn.ELU())
            else:
                print(f'file {file_name} not found')

    def loadModel(self):
        for root, dirs, files in os.walk("../resources/models"):
            if self.modelName in files:
                self.load_state_dict(torch.load(f"{root}/{self.modelName}"))
                self.eval()
                return True
        return False

    def forward(self, x):
        x = self.fc1(x)
        x = self.act1(x)
        x = self.fc2(x)
        x = self.act2(x)
        x = self.fc3(x)
        return x

    def predict_action(self, x):
        x_train = torch.Tensor(x).requires_grad_(True)
        x = x_train.detach().numpy()

        double_x = [x, np.zeros(self.inputN)]
        xi = torch.Tensor(double_x).requires_grad_(True)
        y_prediction = self.nnArc(xi)
        return torch.max(y_prediction[0])

    def predict(self, x, y):
        x = x.detach().numpy()
        y = y.detach().numpy()

        for i in range(self.val_number):
            double_y = [y[i], np.zeros(1)]  # нейросеть обучена для результатов больше чем один вектор
            double_x = [x[i], np.zeros(self.inputN)]
            yi = torch.FloatTensor(double_y)
            xi = torch.Tensor(double_x).requires_grad_(True)
            y_prediction = self.nnArc(xi)
            print(yi, y_prediction)

    @staticmethod
    def loss(prediction, true):
        sq = (prediction - true) ** 2
        return sq.mean()

    def trainBrain(self):

        for param_tensor in self.state_dict():
            print(param_tensor, "\t", self.state_dict()[param_tensor].size())
        optimizer = torch.optim.Adamax(self.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay)
        # Генерация данных для обучения
        if self.modelName:
            self.load_state_dict(torch.load(f"../resources/models/{self.modelName}"))
            self.eval()
        if self.genData:
            f = open(self.genData, )
            [x_train, y_train] = json.load(f)
            y_train = torch.LongTensor(y_train)
            x_train = torch.Tensor(x_train).requires_grad_(True)

            for i_iter in range(self.num_iter):
                optimizer.zero_grad()
                criterion = torch.nn.CrossEntropyLoss()
                y_prediction = self.nnArc(x_train)
                loss = criterion(y_prediction, y_train)
                loss.backward()
                loss_train = float(loss.item())
                optimizer.step()
                print(f'iteration: {i_iter}: {loss_train}')
            # self.predict(x_train[0],y_train[0])

        if self.resave:
            torch.save(self.state_dict(), '../resources/models/model_save.pt')


if __name__ == "__main__":
    net = GameNet("../resources/inputTrain.json")
    net.trainBrain()
