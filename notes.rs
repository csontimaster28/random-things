use std::env;
use std::fs::{OpenOptions, read_to_string};
use std::io::Write;

const FILE_NAME: &str = "notes.txt";

fn add_note(note: &str) {
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(FILE_NAME)
        .expect("Nem sikerült megnyitni a fájlt");

    writeln!(file, "{}", note).expect("Nem sikerült írni a fájlba");
    println!("✅ Jegyzet hozzáadva");
}

fn list_notes() {
    match read_to_string(FILE_NAME) {
        Ok(content) => {
            if content.trim().is_empty() {
                println!("📭 Nincs egy jegyzet sem");
            } else {
                println!("📒 Jegyzetek:\n{}", content);
            }
        }
        Err(_) => println!("📭 Még nincs jegyzet fájl"),
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("Használat:");
        println!("  add <szöveg>   - jegyzet hozzáadása");
        println!("  list          - jegyzetek listázása");
        return;
    }

    match args[1].as_str() {
        "add" => {
            if args.len() < 3 {
                println!("❌ Add meg a jegyzet szövegét");
            } else {
                add_note(&args[2]);
            }
        }
        "list" => list_notes(),
        _ => println!("❌ Ismeretlen parancs"),
    }
}
