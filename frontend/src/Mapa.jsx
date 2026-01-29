import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Coordenadas fixas dos bairros (Garante que o mapa funciona sem o backend mandar lat/lon)
const COORDENADAS = {
    "Acari": [-22.8256, -43.3396],
    "Campo Grande": [-22.9035, -43.5592],
    "Bonsucesso": [-22.8617, -43.2536],
    "Botafogo": [-22.9511, -43.1805],
    "Guadalupe": [-22.8406, -43.3756]
};

const getIconePorRisco = (risco) => {
    let cor = '#22c55e'; // Verde
    let animacao = 'none';
    let tamanho = 18;

    if (risco === 'medio') {
        cor = '#f97316'; // Laranja
        tamanho = 22;
    }
    if (risco === 'alto') {
        cor = '#ef4444'; // Vermelho
        tamanho = 22;
        animacao = 'pulse-red 2s infinite'; // Usa a animação que criamos no CSS
    }

    return L.divIcon({
        className: 'custom-pin',
        html: `<div style="
            background-color: ${cor};
            width: ${tamanho}px;
            height: ${tamanho}px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 0 10px ${cor};
            animation: ${animacao};
        "></div>`,
        iconSize: [tamanho, tamanho],
        iconAnchor: [tamanho / 2, tamanho / 2],
        popupAnchor: [0, -10]
    });
};

const Mapa = ({ dados }) => {
    // Centraliza no Rio de Janeiro
    const centroRJ = [-22.88, -43.35]; 

    return (
        <MapContainer 
            center={centroRJ} 
            zoom={11} 
            style={{ height: '400px', width: '100%', borderRadius: '16px', zIndex: 0 }}
            scrollWheelZoom={false}
        >
            {/* Mapa Dark (Combina com Glassmorphism) */}
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />

            {Object.keys(COORDENADAS).map((bairro) => {
                const latLong = COORDENADAS[bairro];
                const info = dados[bairro] || {};
                const risco = info.nivel_risco || 'baixo';

                return (
                    <Marker 
                        key={bairro} 
                        position={latLong}
                        icon={getIconePorRisco(risco)}
                    >
                        <Popup>
                            <div style={{ textAlign: 'center', color: '#1e293b' }}>
                                <strong>{bairro}</strong><br/>
                                <span style={{ fontSize: '0.9em', textTransform: 'uppercase', fontWeight: 'bold' }}>
                                    {risco}
                                </span>
                                <br/>
                                Chuva: {info.chuva_mm?.toFixed(1) || 0} mm
                            </div>
                        </Popup>
                    </Marker>
                );
            })}
        </MapContainer>
    );
};

export default Mapa;