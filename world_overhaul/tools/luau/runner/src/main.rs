use mlua::{Lua, Result, Table, Value, Function};

fn main() -> Result<()> {
    let lua = Lua::new();
    let globals = lua.globals();
    // read a whole file
    globals.set("__readfile", lua.create_function(|_, p: String| {
        std::fs::read_to_string(&p).map_err(|e| mlua::Error::external(format!("{}: {}", p, e)))
    })?)?;
    // write a whole file
    globals.set("__writefile", lua.create_function(|_, (p, s): (String, mlua::String)| {
        std::fs::write(&p, s.as_bytes()).map_err(|e| mlua::Error::external(format!("{}: {}", p, e)))?;
        Ok(())
    })?)?;
    // compile a file as a function with its own environment table
    globals.set("__loadfile", lua.create_function(|lua, (p, env): (String, Table)| {
        let src = std::fs::read_to_string(&p).map_err(|e| mlua::Error::external(format!("{}: {}", p, e)))?;
        let f: Function = lua.load(&src).set_name(format!("@{}", p)).set_environment(env).into_function()?;
        Ok(f)
    })?)?;
    let args: Vec<String> = std::env::args().collect();
    let argv = lua.create_table()?;
    for (i, a) in args.iter().enumerate().skip(2) { argv.set(i - 1, a.clone())?; }
    globals.set("arg", argv)?;
    let src = std::fs::read_to_string(&args[1]).expect("script");
    let r: Value = lua.load(&src).set_name(format!("@{}", &args[1])).eval()?;
    let _ = r;
    Ok(())
}
