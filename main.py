import json
import shutil
import zipfile
import os


def change(Name, zh, mod_id, authors, description="这是1个mod"):
    java = """package com.thyids.%s;
import com.mojang.logging.LogUtils;
import com.thyids.%s.item.ModItems;
import com.thyids.%s.block.ModBlocks;
import com.thyids.%s.item.ModCreativeModeTabs;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraftforge.event.server.ServerStartingEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
// The value here should match an entry in the META-INF/mods.toml file
@Mod(%s.MOD_ID)
public class %s
{
    // Define mod id in a common place for everything to reference
    public static final String MOD_ID = "%s";
    // Directly reference a slf4j logger
    private static final Logger LOGGER = LogUtils.getLogger();
    public %s()
    {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();
        ModItems.register(modEventBus);
        ModBlocks.register(modEventBus);
        ModCreativeModeTabs.register(modEventBus);
        // Register the commonSetup method for modloading
        modEventBus.addListener(this::commonSetup);
        // Register ourselves for server and other game events we are interested in
        MinecraftForge.EVENT_BUS.register(this);
        // Register the item to a creative tab
        modEventBus.addListener(this::addCreative);
    }
    private void commonSetup(final FMLCommonSetupEvent event) {}
    // Add the example block item to the building blocks tab
    private void addCreative(BuildCreativeModeTabContentsEvent event) {
        
    }
    // You can use SubscribeEvent and let the Event Bus discover methods to call
    @SubscribeEvent
    public void onServerStarting(ServerStartingEvent event) {}
    // You can use EventBusSubscriber to automatically register all static methods in the class annotated with @SubscribeEvent
    @Mod.EventBusSubscriber(modid = MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static class ClientModEvents
    {
        @SubscribeEvent
        public static void onClientSetup(FMLClientSetupEvent event) {}
    }
}
""" % (mod_id, mod_id, mod_id, mod_id, mod_id, Name, mod_id, Name)
    properties = f"""# Sets default memory used for gradle commands. Can be overridden by user or command line properties.
# This is required to provide enough memory for the Minecraft decompilation process.
org.gradle.jvmargs=-Xmx3G
org.gradle.daemon=false
## Environment Properties
# The Minecraft version must agree with the Forge version to get a valid artifact
minecraft_version=1.20.1
# The Minecraft version range can use any release version of Minecraft as bounds.
# Snapshots, pre-releases, and release candidates are not guaranteed to sort properly
# as they do not follow standard versioning conventions.
minecraft_version_range=[1.20.1,1.21)
# The Forge version must agree with the Minecraft version to get a valid artifact
forge_version=47.2.0
# The Forge version range can use any version of Forge as bounds or match the loader version range
forge_version_range=[47,)
# The loader version range can only use the major version of Forge/FML as bounds
loader_version_range=[47,)
# The mapping channel to use for mappings.
# The default set of supported mapping channels are ["official", "snapshot", "snapshot_nodoc", "stable", "stable_nodoc"].
# Additional mapping channels can be registered through the "channelProviders" extension in a Gradle plugin.
#
# | Channel   | Version              |                                                                                |
# |-----------|----------------------|--------------------------------------------------------------------------------|
# | official  | MCVersion            | Official field/method names from Mojang mapping files                          |
# | parchment | YYYY.MM.DD-MCVersion | Open community-sourced parameter names and javadocs layered on top of official |
#
# You must be aware of the Mojang license when using the 'official' or 'parchment' mappings.
# See more information here: https://github.com/MinecraftForge/MCPConfig/blob/master/Mojang.md
#
# Parchment is an unofficial project maintained by ParchmentMC, separate from Minecraft Forge.
# Additional setup is needed to use their mappings, see https://parchmentmc.org/docs/getting-started
mapping_channel=parchment
# The mapping version to query from the mapping channel.
# This must match the format required by the mapping channel.
mapping_version=2023.09.03-1.20.1
## Mod Properties
# The unique mod identifier for the mod. Must be lowercase in English locale. Must fit the regex [a-z][a-z0-9_]{1, 63}
# Must match the String constant located in the main mod class annotated with @Mod.
mod_id={mod_id}
# The human-readable display name for the mod.
mod_name={zh}
# The license of the mod. Review your options at https://choosealicense.com/. All Rights Reserved is the default.
mod_license=All Rights Reserved
# The mod version. See https://semver.org/
mod_version=1.0.0-Minecraft1.20.1-Forge47.2.0
# The group ID for the mod. It is only important when publishing as an artifact to a Maven repository.
# This should match the base package used for the mod sources.
# See https://maven.apache.org/guides/mini/guide-naming-conventions.html
mod_group_id=com.thyids.{mod_id}
# The authors of the mod. This is a simple text string that is used for display purposes in the mod list.
mod_authors={authors}
# The description of the mod. This is a simple multiline text string that is used for display purposes in the mod list.
mod_description={description}"""
    ModItems = """package com.thyids.%s.item;

import com.thyids.%s.%s;
import net.minecraft.world.item.Item;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLLoadCompleteEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, %s.MOD_ID);

    public static void register(IEventBus bus) {
        ITEMS.register(bus);
    }
}""" % (mod_id, mod_id, mod_id, mod_id)
    ModTabs = """package com.thyids.%s.item;

import com.thyids.%s.%s;
import com.thyids.%s.block.ModBlocks;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public class ModCreativeModeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, %s.MOD_ID);

    public static void register(IEventBus bus) {
        CREATIVE_MODE_TABS.register(bus);
    }
}
""" % (mod_id, mod_id, mod_id, mod_id, mod_id)
    ModBlocks = """package com.thyids.%s.block;

import com.thyids.%s.item.ModItems;
import com.thyids.%s.%s;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Supplier;

public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, %s.MOD_ID);

    private static <T extends Block> RegistryObject<T> registerBlock(String name, Supplier<T> block) {
        RegistryObject<T> toReturn = BLOCKS.register(name, block);
        registerBlockItem(name, toReturn);
        return toReturn;
    }

    private static <T extends Block> RegistryObject<Item> registerBlockItem(String name, RegistryObject<T> block) {
        return ModItems.ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
    }

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
    }
}""" % (mod_id, mod_id, mod_id, mod_id, mod_id)
    mods = """# This is an example mods.toml file. It contains the data relating to the loading mods.
# There are several mandatory fields (#mandatory), and many more that are optional (#optional).
# The overall format is standard TOML format, v0.5.0.
# Note that there are a couple of TOML lists in this file.
# Find more information on toml format here:  https://github.com/toml-lang/toml
# The name of the mod loader type to load - for regular FML @Mod mods it should be javafml
modLoader="javafml" #mandatory
# A version range to match for said mod loader - for regular FML @Mod it will be the forge version
loaderVersion="${loader_version_range}" #mandatory This is typically bumped every Minecraft version by Forge. See our download page for lists of versions.
# The license for you mod. This is mandatory metadata and allows for easier comprehension of your redistributive properties.
# Review your options at https://choosealicense.com/. All rights reserved is the default copyright stance, and is thus the default here.
license="${mod_license}"
# A URL to refer people to when problems occur with this mod
#issueTrackerURL="https://change.me.to.your.issue.tracker.example.invalid/" #optional
# A list of mods - how many allowed here is determined by the individual mod loader
[[mods]] #mandatory
# The modid of the mod
modId="%s" #mandatory
# The version number of the mod
version="${mod_version}" #mandatory
# A display name for the mod
displayName="%s" #mandatory
# A URL to query for updates for this mod. See the JSON update specification https://docs.minecraftforge.net/en/latest/misc/updatechecker/
#updateJSONURL="https://change.me.example.invalid/updates.json" #optional
# A URL for the "homepage" for this mod, displayed in the mod UI
#displayURL="https://change.me.to.your.mods.homepage.example.invalid/" #optional
# A file name (in the root of the mod JAR) containing a logo for display
#logoFile="examplemod.png" #optional
# A text field displayed in the mod UI
#credits="感谢下载我的mod" #optional
# A text field displayed in the mod UI
authors="%s" #optional
# Display Test controls the display for your mod in the server connection screen
# MATCH_VERSION means that your mod will cause a red X if the versions on client and server differ. This is the default behaviour and should be what you choose if you have server and client elements to your mod.
# IGNORE_SERVER_VERSION means that your mod will not cause a red X if it's present on the server but not on the client. This is what you should use if you're a server only mod.
# IGNORE_ALL_VERSION means that your mod will not cause a red X if it's present on the client or the server. This is a special case and should only be used if your mod has no server component.
# NONE means that no display test is set on your mod. You need to do this yourself, see IExtensionPoint.DisplayTest for more information. You can define any scheme you wish with this value.
# IMPORTANT NOTE: this is NOT an instruction as to which environments (CLIENT or DEDICATED SERVER) your mod loads on. Your mod should load (and maybe do nothing!) whereever it finds itself.
#displayTest="MATCH_VERSION" # MATCH_VERSION is the default if nothing is specified (#optional)
# The description text for the mod (multi line!) (#mandatory)
description=\"\"\"%s\"\"\"
# A dependency - use the . to indicate dependency for a specific modid. Dependencies are optional.
[[dependencies.${mod_id}]] #optional
    # the modid of the dependency
    modId="forge" #mandatory
    # Does this dependency have to exist - if not, ordering below must be specified
    mandatory=true #mandatory
    # The version range of the dependency
    versionRange="${forge_version_range}" #mandatory
    # An ordering relationship for the dependency - BEFORE or AFTER required if the dependency is not mandatory
    # BEFORE - This mod is loaded BEFORE the dependency
    # AFTER - This mod is loaded AFTER the dependency
    ordering="NONE"
    # Side this dependency is applied on - BOTH, CLIENT, or SERVER
    side="BOTH"
# Here's another dependency
[[dependencies.${mod_id}]]
    modId="minecraft"
    mandatory=true
    # This version range declares a minimum of the current minecraft version up to but not including the next major version
    versionRange="${minecraft_version_range}"
    ordering="NONE"
    side="BOTH"
# Features are specific properties of the game environment, that you may want to declare you require. This example declares
# that your mod requires GL version 3.2 or higher. Other features will be added. They are side aware so declaring this won't
# stop your mod loading on the server for example.
#[features.${mod_id}]""" % (mod_id, zh, authors, description)

    with open(f"project\\{Name}\\gradle.properties", "w", encoding="utf-8") as f:
        f.write(properties)

    with open(f"project\\{Name}\\src\\main\\resources\\META-INF\\mods.toml", "w", encoding="utf-8") as f:
        f.write(mods)

    with open(f"project\\{Name}\\src\\main\\java\\com\\thyids\\test\\Test.java", "w", encoding="utf-8") as f:
        f.write(java)
    with open(f"project\\{Name}\\src\\main\\java\\com\\thyids\\test\\item\\ModItems.java", "w", encoding="utf-8") as f:
        f.write(ModItems)

    with open(f"project\\{Name}\\src\\main\\java\\com\\thyids\\test\\item\\ModCreativeModeTabs.java", "w", encoding="utf-8") as f:
        f.write(ModTabs)
    with open(f"project\\{Name}\\src\\main\\java\\com\\thyids\\test\\block\\ModBlocks.java", "w", encoding="utf-8") as f:
        f.write(ModBlocks)
    # 指定文件夹的当前路径和新路径
    old_folder = os.getcwd() + r"\project\%s\src\main\java\com\thyids\test" % Name
    new_folder = os.getcwd() + r"\project\%s\src\main\java\com\thyids\%s" % (Name, mod_id)

    # 使用os.rename()函数进行重命名
    os.rename(old_folder, new_folder)

    # 指定文件的当前路径和新路径
    old_file = os.getcwd() + r"\project\%s\src\main\java\com\thyids\%s\Test.java" % (Name,
                                                                                                             mod_id)
    new_file = os.getcwd() + r"\project\%s\src\main\java\com\thyids\%s\%s.java" % (Name, mod_id,
                                                                                                           Name)

    # 使用os.rename()函数进行重命名
    os.rename(old_file, new_file)

    # 指定文件夹的当前路径和新路径
    old_folder = os.getcwd() + r"\project\%s\src\main\java\com\thyids" % Name
    new_folder = os.getcwd() + r"\project\%s\src\main\java\com\%s" % (Name, authors)

    # 使用os.rename()函数进行重命名
    os.rename(old_folder, new_folder)

    # 指定文件夹的当前路径和新路径
    old_folder = os.getcwd() + r"\project\%s\src\main\resources\assets\test" % Name
    new_folder = os.getcwd() + r"\project\%s\src\main\resources\assets\%s" % (Name, mod_id)

    # 使用os.rename()函数进行重命名
    os.rename(old_folder, new_folder)

def unzip(file):
    try:
        print("正在生成基础包（大约0-1分钟）")
        with zipfile.ZipFile(os.getcwd()+"\\project.zip", "r") as zip_ref:
            zip_ref.extractall(os.getcwd()+f"\\project\\{file}")
        print("生成基础包完成")
    except Exception as e:
        print("解压失败:", e)

def readlist():
    with open('NameList.json', 'r') as f:
        data = json.load(f)
    return data

def writelist(x, Zhx, modid, Author):
    NameDict = readlist()
    NameDict[x] = {"name":Zhx, "mod_id":modid, "auther":Author, "tabs":{}}
    with open('NameList.json', 'w') as f:
        json.dump(NameDict, f, ensure_ascii=False)

def relist(x, zh_tab="", tab_id="", zhx="", mi="", author=""):
    NameDict = readlist()
    if zhx == "":
        zhx = NameDict[x]["name"]
    if mi == "":
        mi = NameDict[x]["mod_id"]
    if author == "":
        author = NameDict[x]["auther"]
    if zh_tab == "":
        tabs = NameDict[x]["tabs"]
    else:
        tabs = NameDict[x]["tabs"]
        tabs[zh_tab] = tab_id
    NameDict[x] = {"name": zhx, "mod_id": mi, "auther": author, "tabs": tabs}
    with open('NameList.json', 'w') as f:
        json.dump(NameDict, f, ensure_ascii=False)

def delatelist(x):
    NameDict = readlist()
    del NameDict[x]
    with open('NameList.json', 'w') as f:
        json.dump(NameDict, f, ensure_ascii=False)

def build(mod):
    # os.system("echo 请检查根目录不要有旧的jar文件，按任意键继续 && pause -> nul")
    os.system("cd " + os.getcwd() + "\\project\\" + mod + " && " + "gradlew genIntellijRuns")
    os.system("cd " + os.getcwd() + "\\project\\" + mod + " && " + "gradlew jar")
    shutil.copy(
        os.getcwd() + "\\project\\" + mod + "\\build\\libs\\" + mod + "-1.0.0-Minecraft1.20.1-Forge47.2.0.jar",
        mod + "-1.0.0-Minecraft1.20.1-Forge47.2.0.jar")

def change_en_us(mod_id, param, b_name):
    with open("project\\%s\\src\\main\\resources\\assets\\%s\\lang\\en_us.json" % (mod_id, mod_id), "r",
              encoding="utf-8") as file:
        data = json.load(file)

    data[param] = b_name

    with open("project\\%s\\src\\main\\resources\\assets\\%s\\lang\\en_us.json" % (mod_id, mod_id), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def insert_item(mod_id, item_name, item, path, tabs="INGREDIENTS"):
    with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\item\\ModItems.java" % (mod_id, mod_id), "r", encoding="utf-8") as f:
        ModItems = f.readlines()

    for i in range(len(ModItems)):
        if ModItems[i] == "            DeferredRegister.create(ForgeRegistries.ITEMS, %s.MOD_ID);\n" % mod_id:
            ModItems.insert(i + 1,
                            "\n    public static final RegistryObject<Item> %s = ITEMS.register(\"%s\", () -> new Item(new Item.Properties()));" % (
                                item.upper(), item))
            break

    with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\item\\ModItems.java" % (mod_id, mod_id), "w", encoding="utf-8") as f:
        f.writelines(ModItems)


    if tabs == "INGREDIENTS":
        with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\%s.java" % (mod_id, mod_id, mod_id), "r",
                  encoding="utf-8") as f:
            ModItems = f.readlines()

        for i in range(len(ModItems)):
            if ModItems[i] == "    private void addCreative(BuildCreativeModeTabContentsEvent event) {\n":
                ModItems.insert(i + 1,
                                "\n        if(event.getTabKey() == CreativeModeTabs.%s){\n            event.accept(ModItems.%s);\n        }" % (
                                    tabs, item.upper()))
                break

        with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\%s.java" % (mod_id, mod_id, mod_id), "w",
                  encoding="utf-8") as f:
            f.writelines(ModItems)
    else:
        with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\item\\ModCreativeModeTabs.java" % (mod_id, mod_id), "r",
                  encoding="utf-8") as f:
            ModCreativeModeTabs = f.readlines()

        for i in range(len(ModCreativeModeTabs)):
            if "pOutput.accept" in ModCreativeModeTabs[i] or ModCreativeModeTabs[i] in "pOutput.accept":
                ModCreativeModeTabs.insert(i,
                                "\n        pOutput.accept(ModItems.%s.get());\n" % (
                                    item.upper()))
                break

        with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\item\\ModCreativeModeTabs.java" % (mod_id, mod_id), "w",
                  encoding="utf-8") as f:
            f.writelines(ModCreativeModeTabs)

    change_en_us(mod_id,"item.%s.%s" % (mod_id, item),item_name)


    data = {
        "parent": "item/generated",
        "textures": {
            "layer0": "%s:item/%s" % (mod_id, item),
        }
    }

    with open("project\\%s\\src\\main\\resources\\assets\\%s\\models\\item\\%s.json" % (mod_id, mod_id, item), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    os.system("copy %s %s" % (path, "project\\%s\\src\\main\\resources\\assets\\%s\\textures\\item\\%s.png" % (mod_id, mod_id, item)))
    # build(mod_id)


def insert_block(mod_id, block_name, block_id, path, tabs):
    with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\block\\ModBlocks.java" % (mod_id, mod_id), "r",
              encoding="utf-8") as f:
        ModBlocks = f.readlines()

    for i in range(len(ModBlocks)):
        if ModBlocks[i] == "    public static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, %s.MOD_ID);\n" % mod_id:
            ModBlocks.insert(i + 1,
                            """
    public static final RegistryObject<Block> %s = registerBlock("%s",
            () -> new Block(BlockBehaviour.Properties.copy(Blocks.IRON_BLOCK).sound(SoundType.AMETHYST)));""" % (block_id.upper(), block_id))
            break

    with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\block\\ModBlocks.java" % (mod_id, mod_id), "w",
              encoding="utf-8") as f:
        f.writelines(ModBlocks)

    data = {
        "parent": "minecraft:block/cube_all",
        "textures": {
            "all": "%s:block/%s" % (mod_id, block_id),
        }
    }

    with open("project\\%s\\src\\main\\resources\\assets\\%s\\models\\block\\%s.json" % (mod_id, mod_id, block_id), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    data = {
        "parent": "%s:block/%s" % (mod_id, block_id)
    }

    with open("project\\%s\\src\\main\\resources\\assets\\%s\\models\\item\\%s.json" % (mod_id, mod_id, block_id), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


    data = {
        "variants": {
            "": {
                "model": "%s:block/%s" % (mod_id, block_id)
            }
        }
    }

    with open("project\\%s\\src\\main\\resources\\assets\\%s\\blockstates\\%s.json" % (mod_id, mod_id, block_id), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    os.system("copy %s %s" % (path,
                              "project\\%s\\src\\main\\resources\\assets\\%s\\textures\\block\\%s.png" % (mod_id, mod_id,
                                                                                                         block_id)))

    if tabs == "BUILDING_BLOCKS":
        with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\%s.java" % (mod_id, mod_id, mod_id), "r",
                  encoding="utf-8") as f:
            ModItems = f.readlines()

        for i in range(len(ModItems)):
            if ModItems[i] == "    private void addCreative(BuildCreativeModeTabContentsEvent event) {\n":
                ModItems.insert(i + 1,
                                "\n        if(event.getTabKey() == CreativeModeTabs.%s){\n            event.accept(ModBlocks.%s);\n        }" % (
                                    tabs, block_id.upper()))
                break

        with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\%s.java" % (mod_id, mod_id, mod_id), "w",
                  encoding="utf-8") as f:
            f.writelines(ModItems)
    else:
        with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\item\\ModCreativeModeTabs.java" % (mod_id, mod_id), "r",
                  encoding="utf-8") as f:
            ModCreativeModeTabs = f.readlines()

        for i in range(len(ModCreativeModeTabs)):
            if "pOutput.accept" in ModCreativeModeTabs[i] or ModCreativeModeTabs[i] in "pOutput.accept":
                ModCreativeModeTabs.insert(i,
                                "\n        pOutput.accept(ModBlocks.%s.get());\n" % (
                                    block_id.upper()))
                break

        with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\item\\ModCreativeModeTabs.java" % (mod_id, mod_id), "w",
                  encoding="utf-8") as f:
            f.writelines(ModCreativeModeTabs)


    change_en_us(mod_id,"block.%s.%s" % (mod_id, block_id),block_name)

    # build(mod_id)


def insert_bar(mod_id, bar_name, bar, itemid, tabs="INGREDIENTS"):
    relist(mod_id, bar_name, bar)

    with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\item\\ModCreativeModeTabs.java" % (mod_id, mod_id), "r", encoding="utf-8") as f:
        ModItems = f.readlines()

    for i in range(len(ModItems)):
        if ModItems[i] == "            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, %s.MOD_ID);\n" % mod_id:
            ModItems.insert(i + 1,
                            """
    public static final RegistryObject<CreativeModeTab> %s = CREATIVE_MODE_TABS.register("%s", ()-> CreativeModeTab.builder().icon(() -> new ItemStack(ModItems.%s.get())).title(Component.translatable("creativetab.%s")).displayItems((pParameters, pOutput) -> {
        pOutput.accept(ModItems.%s.get());
    }).build());""" % (
                                bar.upper(), bar, itemid.upper(), bar, itemid.upper()))
            break

    with open("project\\%s\\src\\main\\java\\com\\thyids\\%s\\item\\ModCreativeModeTabs.java" % (mod_id, mod_id), "w", encoding="utf-8") as f:
        f.writelines(ModItems)

    change_en_us(mod_id, "creativetab.%s" % bar, bar_name)
    # build(mod_id)


def select_bar(na, zh, en):
    print("1." + zh)
    bar_list = readlist()
    bar_list = list(bar_list[list(bar_list.keys())[na-1]].values())[3]
    for i in range(len(bar_list.keys())):
        print(str(i+2) + "." + list(bar_list.keys())[i])
    ind = int(input("请输入存放物品栏序号："))
    if ind == 1:
        return en
    else:
        return list(bar_list.values())[ind-2]

if __name__ == '__main__':
    print("我的世界1.20.1Forge47.2.0生成器：\n1.创建项目\n2.删除项目\n3.编辑项目")
    select = int(input("输入序号："))
    if select == 1:
        name = input("请输入项目名称（全小写并无特殊字符）:")
        unzip(name)
        ZhName = input("请输入mod中文名:")
        author = input("请输入作者名（用逗号输入多个作者名）:")
        ModId = name
        writelist(name, ZhName, ModId, author)
        change(name, ZhName, ModId, author)
        build(name)
        print("项目创建完成啦！")
    if select == 2:
        ProjectList = readlist()
        for i in range(len(ProjectList.keys())):
            print(str(i+1) + '.' + list(ProjectList.keys())[i])
        ind = int(input("请输入序号："))
        for i in range(len(list(ProjectList[list(ProjectList.keys())[ind-1]].keys()))-1):
            print(list(ProjectList[list(ProjectList.keys())[ind-1]].keys())[i] + ': ' + list(ProjectList[list(ProjectList.keys())[ind-1]].values())[i])
        if_ = input("请确认信息, 是否删除此项目?(Y/N)")
        if if_ == "Y":
            delatelist(list(ProjectList.keys())[ind-1])
            shutil.rmtree(os.getcwd() + "\\project\\" + list(ProjectList.keys())[ind-1])
            print("成功删除项目: " + list(ProjectList.keys())[ind-1])
        else:
            print("您已取消删除操作")
    if select == 3:
        ProjectList = readlist()
        for i in range(len(ProjectList.keys())):
            print(str(i + 1) + '.' + list(ProjectList.keys())[i])
        Name = int(input("请输入序号："))
        print("1.添加")
        print("2.删除")
        print("3.修改")
        print("4.构建")

        ind = int(input("请输入序号："))

        if ind == 1:
            print("1.物品")
            print("2.方块")
            print("3.物品栏")
            ind = int(input("请输入序号："))
            if ind == 1:
                ZhName = input("请输入物品名称（中文）：")
                item_id = input("请输入物品id（仅包括小写字母和下划线）：")
                path_png = input("请输入材质文件路径（png格式）：")
                bar = select_bar(Name, "原材料", "INGREDIENTS")
                insert_item(list(ProjectList[list(ProjectList.keys())[Name-1]].values())[1], ZhName, item_id, path_png, bar)

            elif ind == 2:
                ZhName = input("请输入方块名称（中文）：")
                block_id = input("请输入方块id（仅包括小写字母和下划线）：")
                path_png = input("请输入材质文件路径（png格式）：")
                bar = select_bar(Name, "建筑物品栏", "BUILDING_BLOCKS")
                insert_block(list(ProjectList[list(ProjectList.keys())[Name - 1]].values())[1], ZhName, block_id, path_png, bar)

            elif ind == 3:
                ZhName = input("请输入物品烂名称（中文）：")
                bar_id = input("请输入物品栏id（仅包括小写字母和下划线）：")
                path_png = input("请输入材质名称（从之前的物品或材质获取）：")
                insert_bar(list(ProjectList[list(ProjectList.keys())[Name - 1]].values())[1], ZhName, bar_id, path_png)

        elif ind == 4:
            build(list(ProjectList[list(ProjectList.keys())[Name - 1]].values())[1])