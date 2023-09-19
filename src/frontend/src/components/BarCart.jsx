import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const BarChart = () => {
  const chartRef = useRef(null);
  let myChart = null;

  useEffect(() => {
    const ctx = chartRef.current.getContext("2d");

    const data = {
      labels: ["January", "February", "March", "April", "May"],
      datasets: [
        {
          label: "Monthly Sales",
          data: [1000, 1500, 800, 1200, 2000],
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1,
        },
      ],
    };

    const options = {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    };

    myChart = new Chart(ctx, {
      type: "bar",
      data: data,
      options: options,
    });

    return () => {
      if (myChart) {
        myChart.destroy();
      }
    };
  }, []);

  return (
    <div
      style={{
        width: "450px",
      }}
    >
      <canvas ref={chartRef} style={{ width: "100%", height: "100%" }}></canvas>
    </div>
  );
};

export default BarChart;
