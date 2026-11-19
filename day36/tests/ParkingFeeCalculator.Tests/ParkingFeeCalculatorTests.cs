
using System;
using Xunit;
using ParkingFeeCalculator;

namespace ParkingFeeCalculator.Tests;

public class ParkingFeeCalculatorTests
{
    
    [Theory]
    [InlineData(1, 50)]
    [InlineData(30, 50)]
    [InlineData(60, 50)]
    [InlineData(61, 80)]
    [InlineData(120, 80)]
    [InlineData(121, 110)]
    [InlineData(180, 110)]
    [InlineData(181, 140)]
    [InlineData(240, 140)]
    [InlineData(241, 170)]
    [InlineData(300, 170)]
    [InlineData(301, 200)]
    [InlineData(600, 200)]
    public void CalculateFee_ShouldReturnExpectedFee(
        int parkedMinutes,
        decimal expectedFee)
    {
        // Arrange
        var calculator = new ParkingFeeCalculator();

        // Act
        decimal actualFee = calculator.CalculateFee(parkedMinutes);

        // Assert
        Assert.Equal(expectedFee, actualFee);
    }


    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    [InlineData(-60)]
    public void CalculateFee_ShouldThrowException_WhenDurationIsInvalid(
        int parkedMinutes)
    {
        // Arrange
        var calculator = new ParkingFeeCalculator();

        // Act
        Action act = () => calculator.CalculateFee(parkedMinutes);

        // Assert
        Assert.Throws<ArgumentOutOfRangeException>(act);
    }
}
