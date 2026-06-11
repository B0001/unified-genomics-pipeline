use pluot::prelude::*;

fn main() {
    // Perform a partial read of massive genomic data to prevent memory exhaustion
    // The data remains lazy until the plot actually requires rendering
    let data = Data::from_parquet("s3://biobank/gwas_results.parquet").lazy();
    
    let plot = Plot::new()
       .add_trace(Scatter::new(data.col("p_value"), data.col("effect_size")))
       .interactive(true); // Pluot handles this via rapid static frame generation
    
    // Export the visualization logic to WebAssembly (JavaScript) 
    // to be embedded directly into the clinical frontend
    plot.export_wasm("clinical_dashboard_widget");
}