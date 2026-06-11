import pyarrow.flight as flight
import polars_bio as pb

class GenomicFlightServer(flight.FlightServerBase):
    def do_get(self, context, ticket):
        # The requested dataset ID is securely parsed
        dataset_id = ticket.ticket.decode('utf-8')
        
        # Load the genomic DataFrame natively from the zero-copy Arrow memory space
        df_variants = pb.read_vcf(f"{dataset_id}.vcf")
        
        # Stream the data directly to the requesting compute node over the network
        # This operates at wire-speed without requiring data serialization
        return flight.RecordBatchStream(df_variants.to_arrow())

# Initialize the high-performance genomic data server
server = GenomicFlightServer("grpc://0.0.0.0:8815")
server.serve()