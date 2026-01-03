import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CryptoProvider } from './store';
import Header from './components/Header';
import Overview from './pages/Overview';
import Timeline from './pages/Timeline';
import Analysis from './pages/Analysis';
import Events from './pages/Events';
import About from './pages/About';
<<<<<<< HEAD
=======
import Chatbot from './components/ChatBot';
>>>>>>> origin/main

export default function App() {
  return (
    <CryptoProvider>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/events" element={<Events />} />
          <Route path="/about" element={<About />} />
        </Routes>
        <Chatbot />
      </BrowserRouter>
    </CryptoProvider>
  );
}
