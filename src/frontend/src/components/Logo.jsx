import logo from '../assets/MusicForceLogo.png'

export default function Logo({ size = 40 }) {
  return <img src={logo} alt="MusicForce logo" className="logo" style={{ height: size }} />
}