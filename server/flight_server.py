from __future__ import annotations
import pyarrow.flight as flight
import polars_bio as pb

class GenomicFlightServer(flight.FlightServerBase):
    def do_get(self, context, ticket):
        dataset_id = ticket.ticket.decode("utf-8")
        try:
            df_variants = pb.read_vcf(f"{dataset_id}.vcf")
        except Exception as exc:
            raise flight.FlightServerError(f"Dataset '{dataset_id}' not found: {exc}") from exc
        return flight.RecordBatchStream(df_variants.to_arrow())

def start_server(host: str = "grpc://0.0.0.0", port: int = 8815) -> GenomicFlightServer:
    server = GenomicFlightServer(f"{host}:{port}")
    server.serve()
    return server

if __name__ == "__main__":
    start_server()
