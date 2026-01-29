import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// --- Correção para os ícones do Leaflet não sumirem no React ---
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;
// -------------------------------------------------------------

// Função para criar a "Bolinha Colorida" no mapa
const getIconePorRisco = (risco) => {
    let cor = '#22c55e'; // Verde (Normal)
    
    if (risco === 'medio') cor = '#f97316'; // Laranja
    if (risco === 'alto') cor = '#ef4444'; // Vermelho
    if (!risco) cor = '#94a3b8'; // Cinza (Sem dados)

    return L.divIcon({
        className: 'custom-pin',
        html: `<div style="
            background-color: ${cor};
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.4);
            animation: ${risco === 'alto' ? 'pulse 1.5s infinite' : 'none'};
        "></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12], // Centraliza o ícone
        popupAnchor: [0, -12]
    });
};

const Mapa = ({ dados }) => {
    // Centraliza o mapa numa média aproximada dos bairros do RJ
    const centroRJ = [-22.88, -43.30]; 

    return (
        <div style={{ height: '400px', width: '100%', borderRadius: '16px', overflow: 'hidden', border: '1px solid #334155', marginTop: '20px' }}>
            <MapContainer center={centroRJ} zoom={11} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
                {/* Mapa base escuro (CartoDB Dark Matter) */}
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />

                {/* Gera os pinos para cada bairro */}
                {Object.keys(dados).map((bairro) => {
                    const info = dados[bairro];
                    
                    // Se a API não mandou lat/lon, não desenha
                    if (!info.lat || !info.lon) return null;

                    return (
                        <Marker 
                            key={bairro} 
                            position={[info.lat, info.lon]}
                            icon={getIconePorRisco(info.nivel_risco)}
                        >
                            <Popup className="custom-popup">
                                <div style={{textAlign: 'center'}}>
                                    <strong style={{fontSize: '14px', color: '#0f172a'}}>{bairro}</strong>
                                    <br />
                                    {info.erro ? (
                                        <span style={{color: '#64748b'}}>Sem sinal</span>
                                    ) : (
                                        <>
                                            <span style={{color: '#334155'}}>Chuva: <b>{info.chuva_mm}mm</b></span>
                                            <br/>
                                            <span style={{
                                                color: info.nivel_risco === 'alto' ? '#dc2626' : '#16a34a',
                                                fontWeight: 'bold',
                                                textTransform: 'uppercase',
                                                fontSize: '10px'
                                            }}>
                                                {info.nivel_risco}
                                            </span>
                                        </>
                                    )}
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>
            
            {/* CSS inline para animação de pulso no risco alto */}
            <style>{`
                @keyframes pulse {
                    0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
                    70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
                }
            `}</style>
        </div>
    );
};

export default Mapa;