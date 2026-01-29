import { useEffect, useState } from "react";
import { 
  CloudRain, 
  Droplets, 
  Wind, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Clock,
  MapPin,
  BarChart3,
  History // <--- 1. NOVO IMPORT AQUI
} from "lucide-react";
import Grafico from "./Grafico"; 
import Mapa from "./Mapa"; 
import "./App.css";

const BAIRROS = ["Acari", "Campo Grande", "Bonsucesso", "Botafogo", "Guadalupe"];

function App() {
  const [dadosPorBairro, setDadosPorBairro] = useState({});
  const [carregando, setCarregando] = useState(true);
  const [historico, setHistorico] = useState({});
  const [cardAberto, setCardAberto] = useState(null);

  useEffect(() => {
    const fetchClima = async () => {
      try {
        // OBS: Confirme se sua porta é 8001 mesmo, o padrão do FastAPI costuma ser 8000
        const resp = await fetch("http://127.0.0.1:8000/clima/atual"); 
        const json = await resp.json();
        setDadosPorBairro(json || {});
      } catch (e) {
        console.error(e);
        setDadosPorBairro({});
      } finally {
        setCarregando(false);
      }
    };

    fetchClima();
    const interval = setInterval(fetchClima, 60000);
    return () => clearInterval(interval);
  }, []);

  const toggleGrafico = async (bairro) => {
    if (cardAberto === bairro) {
      setCardAberto(null);
      return;
    }

    setCardAberto(bairro);
    
    if (!historico[bairro]) {
        try {
            const resp = await fetch(`http://127.0.0.1:8000/clima/historico/${bairro}`);
            const json = await resp.json();
            setHistorico(prev => ({ ...prev, [bairro]: json }));
        } catch (error) {
            console.error("Erro ao buscar histórico", error);
        }
    }
  };

  const getStatusInfo = (nivel) => {
    if (nivel === "alto") return { color: "#ef4444", text: "RISCO ALTO", Icon: AlertTriangle };
    if (nivel === "medio") return { color: "#f97316", text: "ATENÇÃO", Icon: AlertTriangle };
    return { color: "#22c55e", text: "NORMAL", Icon: CheckCircle2 };
  };

  if (carregando) return (
    <div className="loading-screen">
      <div className="spinner"></div>
      <p>Sincronizando dados meteorológicos...</p>
    </div>
  );

  return (
    <div className="app">
      <header className="app-header">
        <h1>
          <CloudRain size={32} style={{marginRight: '10px', verticalAlign: 'middle'}} />
          ChuvaAlertaRJ
        </h1>
        <p>Monitoramento em Tempo Real • Rio de Janeiro</p>
      </header>

      <main className="app-main">
        
        <Mapa dados={dadosPorBairro} />
        
        <div style={{ marginBottom: '3rem' }}></div> 

        <div className="grid-bairros">
          {BAIRROS.map((bairro) => {
            const dados = dadosPorBairro ? dadosPorBairro[bairro] : undefined;

            if (!dados || dados.erro) {
              return (
                <div key={bairro} className="card skeleton">
                  <MapPin size={40} className="icon-skeleton" />
                  <h3>{bairro}</h3>
                  <p>Aguardando conexão...</p>
                </div>
              );
            }

            const status = getStatusInfo(dados.nivel_risco);
            const StatusIcon = status.Icon;
            const estaAberto = cardAberto === bairro;

            return (
              <div key={bairro} className="card" style={{ borderColor: status.color }}>
                <div className="card-header">
                  <div className="location-info">
                    <MapPin size={18} className="icon-subtle" />
                    <h2>{bairro}</h2>
                  </div>
                  
                  <div 
                    className="badge-risco" 
                    style={{ backgroundColor: status.color }}
                  >
                    {status.text}
                  </div>
                </div>

                <div className="hora-container">
                  <Clock size={14} />
                  <span>
                    Atualizado às {new Date(dados.horario_registro).toLocaleTimeString("pt-BR", {hour: '2-digit', minute:'2-digit'})}
                  </span>
                </div>

                <div className="metricas">
                  <div className="metrica-item">
                    <div className="metrica-label">
                      <CloudRain size={18} color="#60a5fa" />
                      <span>Chuva (1h)</span>
                    </div>
                    <strong>{dados.chuva_mm?.toFixed(1)} <small>mm</small></strong>
                  </div>

                  <div className="metrica-item">
                    <div className="metrica-label">
                      <Droplets size={18} color="#38bdf8" />
                      <span>Intensidade</span>
                    </div>
                    <strong>{dados.precipitacao?.toFixed(1)} <small>mm/h</small></strong>
                  </div>

                  <div className="metrica-item">
                    <div className="metrica-label">
                      <Wind size={18} color="#94a3b8" />
                      <span>Vento</span>
                    </div>
                    <strong>{dados.vento_velocidade?.toFixed(0)} <small>km/h</small></strong>
                  </div>

                  {/* --- BLOCO NOVO: ACUMULADO PASSADO --- */}
                  <div className="metrica-item">
                    <div className="metrica-label">
                      <History size={18} color="#fbbf24" /> {/* Cor amarela/âmbar */}
                      <span>Acum. 6h</span>
                    </div>
                    <strong>{dados.chuva_acum_6h_ant?.toFixed(1) || '0.0'} <small>mm</small></strong>
                  </div>
                  {/* ------------------------------------- */}

                  <div className="metrica-item">
                    <div className="metrica-label">
                      <TrendingUp size={18} color="#a78bfa" />
                      <span>Prev. 3h</span>
                    </div>
                    <strong>{dados.chuva_acum_3h_prox?.toFixed(1)} <small>mm</small></strong>
                  </div>
                </div>

                <button 
                    onClick={() => toggleGrafico(bairro)}
                    style={{
                        marginTop: '15px',
                        padding: '10px',
                        background: estaAberto ? 'rgba(255,255,255,0.1)' : 'transparent',
                        border: '1px solid #334155',
                        color: 'white',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        transition: '0.2s',
                        width: '100%'
                    }}
                >
                    <BarChart3 size={16} />
                    {estaAberto ? "Ocultar Gráfico" : "Ver Tendência"}
                </button>

                {estaAberto && (
                    <div style={{ animation: 'fadeIn 0.5s' }}>
                        {historico[bairro] ? (
                            <Grafico dados={historico[bairro]} />
                        ) : (
                            <p style={{textAlign: 'center', padding: '20px', fontSize: '0.8rem', opacity: 0.7}}>
                                Carregando histórico...
                            </p>
                        )}
                    </div>
                )}

                <div className="status-footer" style={{ color: status.color, marginTop: '15px' }}>
                  <StatusIcon size={24} />
                  <span>SITUAÇÃO {status.text}</span>
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}

export default App;