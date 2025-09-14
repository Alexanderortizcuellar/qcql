use pgn_reader::{Reader, SanPlus, Skip, Visitor};
use std::env;
use std::{fs::File, io, ops::ControlFlow};
struct GameCounter {
    games: usize,
}

impl Visitor for GameCounter {
    type Tags = ();
    type Movetext = ();
    type Output = ();

    fn begin_tags(&mut self) -> ControlFlow<Self::Output, Self::Tags> {
        ControlFlow::Continue(())
    }

    fn begin_movetext(&mut self, _tags: Self::Tags) -> ControlFlow<Self::Output, Self::Movetext> {
        ControlFlow::Continue(())
    }

    fn san(
        &mut self,
        _movetext: &mut Self::Movetext,
        _san_plus: SanPlus,
    ) -> ControlFlow<Self::Output> {
        ControlFlow::Continue(())
    }

    fn begin_variation(
        &mut self,
        _movetext: &mut Self::Movetext,
    ) -> ControlFlow<Self::Output, Skip> {
        ControlFlow::Continue(Skip(true))
    }

    fn end_game(&mut self, _movetext: Self::Movetext) -> Self::Output {
        self.games += 1;
    }
}

fn main() -> io::Result<()> {
    // open a PGN file instead of a byte cursor
    let filename: String = env::args().nth(1).unwrap();
    let file = File::open(filename)?;
    let mut reader = Reader::new(file);

    let mut counter = GameCounter { games: 0 };

    while reader.read_game(&mut counter)?.is_some() {
        // loop until end of file
    }

    println!("Total games: {}", counter.games);
    Ok(())
}
