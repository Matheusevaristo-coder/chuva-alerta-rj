import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Grafico = ({ dados }) => {
  // 1. Proteção contra dados vazios
  if (!dados || dados.length === 0) {
      return (
        <div style={{ 
            width: '100%', height: '180px', marginTop: '15px', 
            background: 'rgba(0,0,0,0.2)', borderRadius: '12px', 
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column'
        }}>
            <p style={{ color: '#94a3b8', fontSize: '0.8rem', fontWeight: 'bold' }}>Aguardando dados...</p>
        </div>
      );
  }

  // 2. Processamento Flexível (Aceita 'horario' OU 'horario_registro')
  const dadosFormatados = dados.map(item => {
    let horaFormatada = "";
    let chuvaValor = 0;

    // Tenta pegar a CHUVA (se chama 'chuva' ou 'chuva_mm')
    if (item.chuva !== undefined) chuvaValor = item.chuva;
    else if (item.chuva_mm !== undefined) chuvaValor = item.chuva_mm;

    // Tenta pegar o HORÁRIO
    if (item.horario) {
        // Se já vier formatado "17:15", usa direto
        horaFormatada = item.horario;
    } else if (item.horario_registro) {
        // Se vier data completa iso, converte
        try {
            const d = new Date(item.horario_registro);
            if (!isNaN(d.getTime())) {
                horaFormatada = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            }
        } catch (e) {}
    }

    // Se não conseguiu achar hora nenhuma, ignora este item
    if (!horaFormatada) return null;

    return {
        horario: horaFormatada,
        chuva: chuvaValor
    };
  }).filter(x => x !== null);

  // 3. Renderiza o Gráfico
  return (
    <div style={{ 
        width: '100%', 
        marginTop: '15px', 
        background: 'rgba(15, 23, 42, 0.6)', 
        borderRadius: '12px', 
        padding: '10px',
        border: '1px solid rgba(255,255,255,0.05)'
    }}>
      <p style={{ marginBottom: '10px', fontSize: '0.75rem', fontWeight: 'bold', color: '#94a3b8', textAlign: 'center', textTransform: 'uppercase' }}>
        Tendência de Chuva
      </p>

      {/* Wrapper com altura fixa em PIXELS para evitar erro width(-1) */}
      <div style={{ width: '100%', height: '160px' }}>
        <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={dadosFormatados}>
                <defs>
                    <linearGradient id="colorChuva" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                
                <XAxis 
                    dataKey="horario" 
                    tick={{fontSize: 10, fill: '#64748b'}} 
                    axisLine={false} 
                    tickLine={false} 
                    interval="preserveStartEnd"
                />
                
                <YAxis 
                    tick={{fontSize: 10, fill: '#64748b'}} 
                    axisLine={false} 
                    tickLine={false} 
                />
                
                <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                    itemStyle={{ color: '#38bdf8' }}
                    formatter={(value) => [`${value} mm`, 'Chuva']}
                />
                
                <Area 
                    type="monotone" 
                    dataKey="chuva" 
                    stroke="#0ea5e9" 
                    strokeWidth={2} 
                    fill="url(#colorChuva)" 
                    isAnimationActive={true}
                />
            </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Grafico;