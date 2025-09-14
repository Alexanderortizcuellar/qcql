use std::fs;
use regex::Regex;
use std::env;

fn main() -> std::io::Result<()> {
    let filename = env::args().nth(1).unwrap();
    let text = fs::read_to_string(filename.as_str())?;
    let re = Regex::new(r"(?m)^\[Event\s").unwrap();

    let count = re.find_iter(&text).count();
    println!("Total games: {}", count);

    Ok(())
}
 