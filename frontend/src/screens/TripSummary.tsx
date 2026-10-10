import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, EmptyState, Heading, Screen } from "../components/ui";
import { useTrip } from "../state/trip";

export function TripSummary() {
  const navigate = useNavigate();
  const { trip, reset } = useTrip();

  useEffect(() => {
    if (!trip) navigate("/");
  }, [trip, navigate]);

  if (!trip) {
    return (
      <Screen>
        <EmptyState title="No trip yet" body="Tap in at a station to start." />
      </Screen>
    );
  }

  return (
    <Screen>
      <Heading kicker="Trip" title="You are set" />
      <Card>
        <p className="text-[18px] leading-7 text-ink">{trip.summary}</p>
        <dl className="mt-8 grid gap-4 text-[15px] md:grid-cols-3">
          <div>
            <dt className="text-mute">Wait</dt>
            <dd className="mt-1 text-[22px] font-medium">{trip.wait_minutes} min</dd>
          </div>
          <div>
            <dt className="text-mute">Door to door</dt>
            <dd className="mt-1 text-[22px] font-medium">{trip.door_to_door_minutes} min</dd>
          </div>
          <div>
            <dt className="text-mute">Fare</dt>
            <dd className="mt-1 text-[22px] font-medium">{trip.assignment.fare_inr} INR</dd>
          </div>
        </dl>
      </Card>
      <div className="mt-8">
        <Button
          onClick={() => {
            reset();
            navigate("/");
          }}
        >
          New ride
        </Button>
      </div>
    </Screen>
  );
}
