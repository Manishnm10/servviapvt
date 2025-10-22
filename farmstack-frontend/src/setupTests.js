import React from "react";
import { createRoot } from "react-dom/client";
import "./Assets/CSS/common.css";
import App from "./App";
import FarmStackProvider from "./Components/Contexts/FarmStackContext";

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <FarmStackProvider>
    <App />
  </FarmStackProvider>
);