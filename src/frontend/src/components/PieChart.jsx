import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const PieChart = () => {
  const chartRef = useRef(null);
  let myChart = null;

  useEffect(() => {
    const ctx = chartRef.current.getContext("2d");

    const data = {
      labels: ["Red", "Blue", "Yellow", "Green", "Purple"],
      datasets: [
        {
          data: [12, 19, 3, 5, 2],
          backgroundColor: [
            "rgba(255, 99, 132, 0.7)",
            "rgba(54, 162, 235, 0.7)",
            "rgba(255, 206, 86, 0.7)",
            "rgba(75, 192, 192, 0.7)",
            "rgba(153, 102, 255, 0.7)",
          ],
        },
      ],
    };

    myChart = new Chart(ctx, {
      type: "pie",
      data: data,
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
        width: "300px",
      }}
    >
      <canvas ref={chartRef} style={{ width: "100%", height: "100%" }}></canvas>
    </div>
  );
};

export default PieChart;
