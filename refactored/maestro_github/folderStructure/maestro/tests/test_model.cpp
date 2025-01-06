#include "gtest/gtest.h"
#include "model.cpp"
#include <vector>

TEST(NeuralNetworkTest, Construction) {
  NeuralNetwork nn(10, 2); // Input size 10, output size 2
  ASSERT_NE(nullptr, &nn); // Check if object is created
}

TEST(NeuralNetworkTest, TrainValidData) {
    NeuralNetwork nn(2,1);
    std::vector<std::vector<double>> input = {{1.0, 2.0}, {3.0,4.0}};
    std::vector<std::vector<double>> target = {{3.0}, {7.0}};
    ASSERT_NO_THROW(nn.train(input, target));
}

TEST(NeuralNetworkTest, TrainInvalidDataDifferentSizes) {
    NeuralNetwork nn(2,1);
    std::vector<std::vector<double>> input = {{1.0, 2.0}, {3.0,4.0}};
    std::vector<std::vector<double>> target = {{3.0}};
    ASSERT_THROW(nn.train(input, target), std::runtime_error);
}

TEST(NeuralNetworkTest, TrainInvalidDataEmpty) {
    NeuralNetwork nn(2, 1);
    std::vector<std::vector<double>> input = {};
    std::vector<std::vector<double>> target = {};
    ASSERT_THROW(nn.train(input, target), std::runtime_error);
}

TEST(NeuralNetworkTest, TrainInvalidDataDimensions) {
    NeuralNetwork nn(2, 1);
    std::vector<std::vector<double>> input = {{1.0, 2.0, 3.0}, {4.0, 5.0, 6.0}};
    std::vector<std::vector<double>> target = {{3.0}, {7.0}};
    ASSERT_THROW(nn.train(input, target), std::runtime_error);
}