import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import FirstPage from './FirstPage';
import BlueBin from './BlueBin';
import RealtimeDetect from './RealtimeDetect';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<RealtimeDetect />} />
          <Route path="/blueBin" element={<BlueBin />} /> {/* เส้นทางสำหรับหน้า SecondPage */}
          {/* <Route path="/" element={<FirstPage />} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
