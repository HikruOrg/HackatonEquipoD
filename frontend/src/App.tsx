import React from "react";
import ClassifierPage from "./ClassifierPage";
import { ThemeProvider } from "./ThemeContext";

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <ClassifierPage />
    </ThemeProvider>
  );
};

export default App;