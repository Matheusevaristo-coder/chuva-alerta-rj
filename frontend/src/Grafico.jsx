import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Grafico = ({ dados }) => {
  if (!dados || dados.length === 0) return <p style={{textAlign: 'center', opacity: 0.5}}>Sem histórico</p>;

  return (
    <div style={{ width: '100%', height: 200, marginTop: '20px' }}>
      <p style={{ marginBottom: '10px', fontSize: '0.9rem', fontWeight: 'bold' }}>Tendência de Chuva (mm)</p>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={dados}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorChuva" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#60a5fa" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#60a5fa" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis 
            dataKey="horario" 
            tick={{fontSize: 12, fill: '#94a3b8'}} 
            axisLine={false}
            tickLine={false}
          />
          <YAxis 
            tick={{fontSize: 12, fill: '#94a3b8'}} 
            axisLine={false}
            tickLine={false}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }}
            itemStyle={{ color: '#fff' }}
          />
          <Area 
            type="monotone" 
            dataKey="chuva" 
            stroke="#60a5fa" 
            fillOpacity={1} 
            fill="url(#colorChuva)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default Grafico;