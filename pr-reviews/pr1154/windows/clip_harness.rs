#![cfg(windows)]
// VM-only harness: put a drawing on the clipboard through the app's real copy
// path, read it back through the real paste path, and check picture files.
#[tokio::test]
#[ignore = "manual clipboard harness"]
async fn clip_harness() {
    reshiki_windows::enable_office_embedding();
    let path = std::env::var("CLIP_RSK").unwrap();
    let image_only = std::env::var("CLIP_IMAGE_ONLY").is_ok_and(|v| v == "1");
    let doc = reshiki::document::Document::from_native_file(&std::fs::read(path).unwrap()).unwrap();
    let outcome = reshiki::clipboard::copy(reshiki::engine::LocalEngine::default(), doc, image_only)
        .await
        .unwrap();
    println!("image_only={image_only} external_editable={} notices={:?}", outcome.external_editable, outcome.notices);
}

#[tokio::test]
#[ignore = "manual clipboard harness"]
async fn clip_paste() {
    reshiki_windows::enable_office_embedding();
    for image_only in [false, true] {
        match reshiki::clipboard::paste_with_warnings(reshiki::engine::LocalEngine::default(), image_only).await {
            Ok(outcome) => println!(
                "paste image_only={image_only} native={} atoms={} bonds={} pictures={} warnings={:?}",
                outcome.native,
                outcome.document.atoms.len(),
                outcome.document.bonds.len(),
                outcome.document.graphics.iter().filter(|g| g.picture.is_some()).count(),
                outcome.warnings
            ),
            Err(error) => println!("paste image_only={image_only} error={error}"),
        }
    }
}

#[test]
#[ignore = "manual clipboard harness"]
fn file_payload() {
    for path in std::env::var("CLIP_FILES").unwrap().split(';').filter(|p| !p.is_empty()) {
        let bytes = std::fs::read(path).unwrap();
        let result = match reshiki::payload::read(&bytes) {
            None => "none".to_owned(),
            Some(Ok(doc)) => format!("drawing atoms={} bonds={}", doc.atoms.len(), doc.bonds.len()),
            Some(Err(error)) => format!("damaged: {error}"),
        };
        println!("file {path} bytes={} payload={result}", bytes.len());
    }
}
