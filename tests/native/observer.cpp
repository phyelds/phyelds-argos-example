// Test observer only: the aggregate programs never see these global positions.
#include <argos3/core/simulator/simulator.h>
#include <argos3/core/simulator/space/space.h>
#include <argos3/core/utility/plugins/dynamic_loading.h>
#include <argos3/plugins/robots/foot-bot/simulator/footbot_entity.h>
#include <argos3/plugins/simulator/entities/led_equipped_entity.h>
#include <iostream>
#include <argos3/core/utility/logging/argos_log.h>
#include <iomanip>

void Snapshot(argos::CSimulator& simulator) {
    auto& space = simulator.GetSpace();
    for (auto& item : space.GetEntitiesByType("foot-bot")) {
        auto* robot = argos::any_cast<argos::CFootBotEntity*>(item.second);
        auto& anchor = robot->GetEmbodiedEntity().GetOriginAnchor();
        argos::CRadians yaw, pitch, roll;
        anchor.Orientation.ToEulerAngles(yaw, pitch, roll);
        auto color = robot->GetLEDEquippedEntity().GetLED(0).GetColor();
        std::cout << "POSE " << space.GetSimulationClock() << ' ' << robot->GetId() << ' '
            << std::setprecision(10) << anchor.Position.GetX() << ' ' << anchor.Position.GetY() << ' '
            << yaw.GetValue() << ' ' << int(color.GetRed()) << ' ' << int(color.GetGreen()) << ' '
            << int(color.GetBlue()) << '\n';
    }
}

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    argos::LOG.DisableColoredOutput();
    argos::LOGERR.DisableColoredOutput();
    try {
        argos::CDynamicLoading::LoadAllLibraries();
        auto& simulator = argos::CSimulator::GetInstance();
        simulator.SetExperimentFileName(argv[1]);
        simulator.LoadExperiment(true);
        Snapshot(simulator);
        while (!simulator.IsExperimentFinished()) {
            simulator.UpdateSpace();
            if (simulator.GetSpace().GetSimulationClock() % 10 == 0) Snapshot(simulator);
        }
        simulator.Destroy();
    } catch (std::exception const& error) {
        std::cerr << error.what() << std::endl;
        return 1;
    }
}
