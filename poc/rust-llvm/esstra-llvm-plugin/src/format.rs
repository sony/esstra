//! ESSTRA Format module
//!
//! This module includes the code related to ESSTRA data format

fn escape_for_asm(data: &str) -> String {
    data.chars()
        .flat_map(|c| {
            if c == '\\' {
                vec!['\\', '\\']
            } else if c == '"' {
                vec!['\\', '"']
            } else if c == '\t' {
                vec!['\\', 't']
            } else {
                vec![c]
            }
        })
        .collect::<String>()
}

/// Process string data for embedding as assembly
pub fn process_data_for_asm(data: &str) -> String {
    let mut res = String::from("\t.pushsection .esstra\n");
    for line in data.lines() {
        let line = escape_for_asm(line);
        res.push_str(&format!("\t.ascii \"{line}\\n\"\n"));
    }
    res.push_str("\t.popsection\n");
    res
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_escape_for_asm() {
        let data = "\tescape\n\\\"me\\\"";
        // Do not escape \n because `escape_for_asm` expects one-line string
        assert_eq!(escape_for_asm(data), "\\tescape\n\\\\\\\"me\\\\\\\"");
    }

    // Simply check that the assembly embedding will work correctly
    #[test]
    fn validate_asm() {
        let asm = crate::format::process_data_for_asm("line1\nline2");
        assert_eq!(
            asm,
            "\t.pushsection .esstra\n\t.ascii \"line1\\n\"\n\t.ascii \"line2\\n\"\n\t.popsection\n"
        );
    }
}
