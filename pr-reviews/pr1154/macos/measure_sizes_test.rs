// Not committed: measures #462 payload and clipboard sizes; also writes the
// test drawings as .rsk files for the survival checks.
use super::*;
use crate::document::Point;

async fn import(engine: &LocalEngine, text: &str) -> Document {
    engine.request(text_request(text)).await.unwrap().document.unwrap()
}

fn noise_png(side: u32) -> Vec<u8> {
    let mut state = 0x2545_f491_u32;
    let pixels: Vec<u8> = (0..side * side * 3)
        .map(|_| {
            state ^= state << 13;
            state ^= state >> 17;
            state ^= state << 5;
            state as u8
        })
        .collect();
    let mut bytes = Vec::new();
    {
        let mut encoder = png::Encoder::new(&mut bytes, side, side);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.write_header().unwrap().write_image_data(&pixels).unwrap();
    }
    bytes
}

#[tokio::test]
#[ignore = "manual measurement"]
async fn measure_462_sizes() {
    let engine = LocalEngine::default();
    let out = std::path::PathBuf::from(std::env::var("MEASURE_OUT").unwrap());
    std::fs::create_dir_all(&out).unwrap();
    let caffeine = import(&engine, "CN1C=NC2=C1C(=O)N(C(=O)N2C)C").await;
    let reaction = import(&engine, "CC(=O)O.OCC>>CC(=O)OCC.O").await;
    let atorvastatin = "CC(C)c1c(C(=O)Nc2ccccc2)c(-c2ccccc2)c(-c2ccc(F)cc2)n1CC[C@@H](O)C[C@@H](O)CC(=O)O";
    let big = import(&engine, &[atorvastatin; 5].join(".")).await;
    let mut photo = caffeine.clone();
    let png = noise_png(1300);
    let picture = crate::pictures::Picture::import(&png).unwrap();
    let id = photo.next_id();
    photo.graphics.push(picture.graphic(id, Point::new(0., 200.)));
    println!("photo source png bytes={}", png.len());
    for (name, doc) in [("caffeine", caffeine), ("reaction", reaction), ("atorvastatin-x5", big), ("caffeine-photo", photo)] {
        std::fs::write(out.join(format!("{name}.rsk")), doc.file_json().unwrap()).unwrap();
        let native = serde_json::to_vec(&doc.current()).unwrap().len();
        let envelope = crate::payload::encode(&doc).unwrap().len();
        print!("{name}: atoms={} native_json={native} envelope={envelope}", doc.atoms.len());
        for image_only in [false, true] {
            let (outcome, reps) = match prepare_copy_for(engine.clone(), doc.clone(), image_only, false).await { Ok(v) => v, Err(e) => { print!(" | image_only={image_only} error={e}"); continue; } };
            let sizes: Vec<_> = reps.iter().map(|r| (r.kind.clone(), r.bytes().map(|b| b.len()).map_err(|e| e))).collect();
            let total: usize = sizes.iter().filter_map(|(_, n)| n.as_ref().ok()).sum();
            let label = if image_only { "copy_image" } else { "copy" };
            print!(" | {label} total={total} {:?} notices={:?}", sizes, outcome.notices);
            if let Some(png) = reps.iter().find(|r| r.kind == "public.png") {
                if let Ok(bytes) = png.bytes() { std::fs::write(out.join(format!("{name}-{label}.png")), bytes).unwrap(); }
            }
        }
        println!();
    }
}
