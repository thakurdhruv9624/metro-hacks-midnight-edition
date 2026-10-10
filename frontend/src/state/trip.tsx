import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import type { Station, Trip } from "../lib/api";

type TripState = {
  station: Station | null;
  trip: Trip | null;
  setStation: (station: Station) => void;
  setTrip: (trip: Trip) => void;
  reset: () => void;
};

const Ctx = createContext<TripState | null>(null);

export function TripProvider({ children }: { children: ReactNode }) {
  const [station, setStation] = useState<Station | null>(null);
  const [trip, setTrip] = useState<Trip | null>(null);
  const value = useMemo(
    () => ({
      station,
      trip,
      setStation,
      setTrip,
      reset: () => {
        setStation(null);
        setTrip(null);
      },
    }),
    [station, trip],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useTrip() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useTrip must be used within TripProvider");
  return ctx;
}
