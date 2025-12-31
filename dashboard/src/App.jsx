import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Overview from './pages/Overview';
import Timeline from './pages/Timeline';
import Analysis from './pages/Analysis';
import Events from './pages/Events';

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Overview />} />
        <Route path="/timeline" element={<Timeline />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/events" element={<Events />} />
      </Routes>
    </BrowserRouter>
  );
}
