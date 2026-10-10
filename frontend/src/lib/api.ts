const BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export type Station = {
  id: string;
  name: string;
  line: string;
  lat: number;
  lng: number;
  bays: number;
  zone: string;
};

export type DropZone = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  aliases: string[];
};

export type Trip = {
  id: string;
  station_id: string;
  station_name: string;
  drop: { zone_id: string; zone_name: string; lat: number; lng: number; confidence: number; source: string };
  assignment: {
    bay: number;
    slot_start: string;
    slot_end: string;
    vehicle_id: string;
    vehicle_type: "e-auto" | "feeder-bus";
    group_id: string;
    group_size: number;
    fare_inr: number;
    walk_minutes: number;
    eta_minutes: number;
  };
  summary: string;
  status: string;
  created_at: string;
  door_to_door_minutes: number;
  wait_minutes: number;
};

export type Dashboard = {
  generated_at: string;
  city_avg_wait: number;
  city_occupancy: number;
  stations: {
    station_id: string;
    station_name: string;
    predicted_exits: number;
    vehicles_available: number;
    occupancy_pct: number;
    avg_wait_minutes: number;
    heat: number;
  }[];
  vehicles: {
    vehicle_id: string;
    vehicle_type: string;
    station_id: string;
    occupancy: number;
    capacity: number;
    status: string;
  }[];
};

export type Comparison = {
  generated_at: string;
  narrative: string;
  metrics: { label: string; unit: string; baseline: number; metrosync: number; delta_pct: number }[];
};

export const api = {
  stations: () => request<{ stations: Station[]; drop_zones: DropZone[] }>("/stations"),
  createTrip: (station_id: string, drop_text: string) =>
    request<Trip>("/rider/trip", {
      method: "POST",
      body: JSON.stringify({ station_id, drop_text, party_size: 1 }),
    }),
  trip: (id: string) => request<Trip>(`/rider/trip/${id}`),
  dashboard: () => request<Dashboard>("/dashboard"),
  comparison: () => request<Comparison>("/comparison"),
};
