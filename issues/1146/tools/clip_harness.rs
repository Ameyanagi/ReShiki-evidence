#![cfg(windows)]
// VM-only harness: put a drawing on the clipboard through the app's real copy path.
#[tokio::test]
#[ignore = "manual clipboard harness"]
async fn clip_harness() {
    reshiki_windows::enable_office_embedding();
    let path = std::env::var("CLIP_RSK").unwrap();
    let image_only = std::env::var("CLIP_IMAGE_ONLY").is_ok_and(|v| v == "1");
    let doc = reshiki::document::Document::from_json(&std::fs::read(path).unwrap()).unwrap();
    let outcome = reshiki::clipboard::copy(reshiki::engine::LocalEngine::default(), doc, image_only)
        .await
        .unwrap();
    println!("image_only={image_only} external_editable={} notices={:?}", outcome.external_editable, outcome.notices);
}
