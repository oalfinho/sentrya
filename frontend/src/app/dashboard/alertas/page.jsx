"use client";

import { AlertCard } from "@/components/alerts/AlertCard";
import { CriticalTable } from "@/components/alerts/CriticalTable";
import { RecommendationCard } from "@/components/alerts/RecommendationCard";
import { RiskPanel } from "@/components/alerts/RiskPanel";
import { useSensorData } from "@/hooks/useSensorData";

export default function AlertsPage() {
  const { data, events, anomalies } = useSensorData();

  // Monta lista de alertas a partir dos eventos acumulados do WS
 const alerts = events
  .filter((ev) => ev != null)
  .map((ev) => ({
    id: ev.id,
    title: ev.title,
    location: ev.sensor_id,
    sector: "Monitorado",
    time: ev.timestamp
      ? new Date(ev.timestamp).toLocaleTimeString("pt-BR")
      : "—",
    sensor: ev.sensor_id,
    aiConfidence: Math.round((data?.anomaly_score ?? 0) * 100),
    isolationScore: data?.anomaly_score?.toFixed(3) ?? "—",
    estimatedFailure: "—",
    currentVibration: Number(data?.vibracao ?? 0).toFixed(4),
    severity: ev.level === "danger" ? "critical" : "alert",
    insight: ev.desc,
  }));

  // Máquinas críticas para a tabela — baseado nas anomalias do IF
  const critical = anomalies.slice(0, 5).map((a, i) => ({
    id: String(i),
    status: a.label === "Crítico" ? "critico" : "falha-progressiva",
    machine: a.sensor_id,
    risk: Math.round(a.anomaly_score * 100),
    trend: "up",
  }));

  const validEvents = (events || []).filter((e) => e != null);

  const criticalCount = validEvents.filter((e) => e.level === "danger").length;
  const progressiveCount = validEvents.filter((e) => e.level === "warn").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-brand-cream">
          Central de Alertas
        </h2>
        <p className="mt-1 font-mono text-[11px] text-brand-muted">
          Eventos Alerta e Crítico detectados pelo Isolation Forest
        </p>
      </div>

      {/* Painel de risco + recomendação */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RiskPanel
            riskPercentage={Math.round((data?.anomaly_score ?? 0) * 100)}
            criticalMachines={criticalCount}
            progressiveFailures={progressiveCount}
            urgentMaintenance={criticalCount}
          />
        </div>
        <RecommendationCard
          message={
            data?.is_anomaly
              ? "Verificar rolamentos e componentes mecânicos do sensor em alerta"
              : "Sistema dentro dos padrões normais — manutenção preventiva em dia"
          }
          priority={
            data?.status === "CRITICO"
              ? "high"
              : data?.status === "ALERTA"
                ? "medium"
                : "low"
          }
        />
      </div>

      {/* Tabela de críticos */}
      {critical.length > 0 && <CriticalTable machines={critical} />}

      {/* Cards de alerta */}
      {alerts.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-16">
          <p className="font-mono text-[13px] text-brand-muted">
            Nenhum alerta registrado nesta sessão
          </p>
          <p className="font-mono text-[11px] text-brand-muted/50">
            Os alertas aparecem aqui quando o IF detectar anomalias via
            WebSocket
          </p>
        </div>
      ) : (
        <div>
          {alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      )}
    </div>
  );
}
