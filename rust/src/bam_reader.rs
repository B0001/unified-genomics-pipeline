// Cargo.toml dependencies:
// cargo add noodles --features bam,sam,bgzf,core

use noodles::bam;
use noodles::bgzf;
use std::fs::File;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // High-speed, fearless concurrency reading of compressed BAM data
    let mut reader = File::open("sample.bam")
       .map(bgzf::Reader::new)
       .map(bam::Reader::new)?;

    let header = reader.read_header()?;
    
    for result in reader.records(&header) {
        let record = result?;
        // At this stage, libraries like datafusion-bio-formats can stream 
        // these records directly into a zero-copy Apache Arrow memory space.
    }
    Ok(())
}